# -*- coding: utf-8 -*-
from random import choice
from StringIO import StringIO
from pkg_resources import resource_filename

from zope.interface import implements
import sqlalchemy as sa
import sqlalchemy.orm.exc as orm_exc

from lxml import etree
from lxml.builder import ElementMaker

from PIL import Image
import mapscript

from nextgisweb.models import declarative_base
from nextgisweb.resource import (
    Resource,
    ResourceScope,
    DataScope,
    Serializer,
    SerializedProperty as SP)
from nextgisweb.resource.exception import ValidationError
from nextgisweb.env import env
from nextgisweb.geometry import box
from nextgisweb.feature_layer import IFeatureLayer, GEOM_TYPE
from nextgisweb.marker_library import Marker
from nextgisweb.render import (
    IRenderableStyle,
    IExtentRenderRequest,
    ITileRenderRequest,
    ILegendableStyle,
)

from .mapfile import Map, mapfile, schema, registry

from .util import _

Base = declarative_base()

# Палитра из 12 цветов ColorBrewer
_RNDCOLOR = (
    (141, 211, 199),
    (255, 255, 179),
    (190, 186, 218),
    (251, 128, 114),
    (128, 177, 211),
    (253, 180, 98),
    (179, 222, 105),
    (252, 205, 229),
    (217, 217, 217),
    (188, 128, 189),
    (204, 235, 197),
    (255, 237, 111),
)


class RenderRequest(object):
    implements(IExtentRenderRequest, ITileRenderRequest)

    def __init__(self, style, srs, cond):
        self.style = style
        self.srs = srs
        self.cond = cond

    def render_extent(self, extent, size):
        return self.style.render_image(self.srs, extent, size, self.cond)

    def render_tile(self, tile, size):
        extent = self.srs.tile_extent(tile)
        return self.style.render_image(
            self.srs, extent, (size, size),
            self.cond,
            padding=size / 2
        )


class MapserverStyle(Base, Resource):
    identity = 'mapserver_style'
    cls_display_name = _("MapServer style")

    __scope__ = DataScope

    implements(IRenderableStyle, ILegendableStyle)

    xml = sa.Column(sa.Unicode, nullable=False)

    @classmethod
    def check_parent(cls, parent):
        return IFeatureLayer.providedBy(parent)

    @property
    def feature_layer(self):
        return self.parent

    @property
    def srs(self):
        return self.parent.srs

    def render_request(self, srs, cond=None):
        return RenderRequest(self, srs, cond)

    @classmethod
    def default_style_xml(cls, layer):
        E = ElementMaker()

        style = E.style(
            E.color(dict(zip(
                ('red', 'green', 'blue'), map(str, choice(_RNDCOLOR))
            ))),
            E.outlinecolor(red='64', green='64', blue='64'),
        )

        legend = E.legend(
            E.keysize(x='15', y='15'),
            E.label(
                E.size('12'),
                E.type('truetype'),
                E.font('regular')
            )
        )

        root = E.map(
            E.layer(
                E('class', style)
            ),
            legend
        )

        if layer.geometry_type == GEOM_TYPE.POINT or (
            hasattr(GEOM_TYPE, 'MULTIPOINT') and
                layer.geometry_type == GEOM_TYPE.MULTIPOINT):
            symbol = E.symbol(
                E.type('ellipse'),
                E.name('circle'),
                E.points('1 1'),
                E.filled('true'),
            )

            root.insert(0, symbol)

            style.append(E.symbol('circle'))
            style.append(E.size('6'))

        return etree.tostring(root, pretty_print=True)

    def render_image(self, srs, extent, size, cond, padding=0):
        res_x = (extent[2] - extent[0]) / size[0]
        res_y = (extent[3] - extent[1]) / size[1]

        # Экстент с учетом отступов
        extended = (
            extent[0] - res_x * padding,
            extent[1] - res_y * padding,
            extent[2] + res_x * padding,
            extent[3] + res_y * padding,
        )

        # Размер изображения с учетом отступов
        render_size = (
            size[0] + 2 * padding,
            size[1] + 2 * padding
        )

        # Фрагмент изображения размера size
        target_box = (
            padding,
            padding,
            size[0] + padding,
            size[1] + padding
        )

        # Выбираем объекты по экстенту
        feature_query = self.parent.feature_query()

        # Отфильтровываем объекты по условию
        if cond is not None:
            feature_query.filter_by(**cond)

        # FIXME: Тоже самое, но через интерфейсы
        if hasattr(feature_query, 'srs'):
            feature_query.srs(srs)

        feature_query.intersects(box(*extended, srid=srs.id))
        feature_query.geom()
        features = feature_query()

        if features.total_count < 1:
            return Image.new('RGBA', (size[0], size[1]), (255, 255, 255, 0))

        mapobj = self._mapobj(features)

        # Получаем картинку эмулируя WMS запрос
        req = mapscript.OWSRequest()
        req.setParameter("bbox", ','.join(map(str, extended if padding else extent)))
        req.setParameter("width", str(render_size[0]))
        req.setParameter("height", str(render_size[1]))
        req.setParameter("srs", 'EPSG:%d' % self.parent.srs_id)
        req.setParameter("format", 'image/png')
        req.setParameter("layers", 'main')
        req.setParameter("request", "GetMap")
        req.setParameter('transparent', 'TRUE')

        mapobj.loadOWSParameters(req)
        gdimg = mapobj.draw()

        # Преобразуем изображение из PNG в объект PIL
        buf = StringIO()
        buf.write(gdimg.getBytes())
        buf.seek(0)

        img = Image.open(buf)

        # Вырезаем нужный нам кусок изображения
        return img.crop(target_box)

    def render_legend(self):
        mapobj = self._mapobj(features=[])
        gdimg = mapobj.drawLegend()

        buf = StringIO()
        buf.write(gdimg.getBytes())
        buf.seek(0)

        return buf

    def _mapobj(self, features):
        # tmpf = NamedTemporaryFile(suffix='.map')
        # buf = codecs.open(tmpf.name, 'w', 'utf-8')
        buf = StringIO()

        fieldnames = map(lambda f: f.keyname, self.parent.fields)

        E = ElementMaker()

        # Настраиваем map
        emap = etree.fromstring(self.xml)

        map_setup = [
            E.size(width='800', height='600'),
            E.maxsize('4096'),
            E.imagecolor(red='255', green='255', blue='255'),
            E.imagetype('PNG'),
            E.outputformat(
                E.name('png'),
                E.extension('png'),
                E.mimetype('image/png'),
                E.driver('AGG/PNG'),
                E.imagemode('RGBA'),
                E.formatoption('INTERLACE=OFF')
            ),
            E.web(
                E.metadata(
                    E.item(
                        key='wms_onlineresource',
                        value='http://localhost/'
                    ),
                    E.item(
                        key='wfs_onlineresource',
                        value='http://localhost/'
                    ),
                    E.item(
                        key='ows_title',
                        value='nextgisweb'
                    ),
                    E.item(
                        key='wms_enable_request',
                        value='*'
                    ),
                    E.item(
                        key='wms_srs',
                        value='EPSG:3857'
                    )
                )
            ),
            E.extent(minx='-180', miny='-90', maxx='180', maxy='90'),
            E.projection("+init=epsg:4326"),
            E.fontset(env.mapserver.settings['fontset']),
            E.symbolset(resource_filename(
                'nextgisweb_mapserver', 'symbolset'
            ))
        ]

        for i in reversed(map_setup):
            emap.insert(0, i)

        # Настраиваем layer
        elayer = emap.find('./layer')

        layer_setup = [
            E.name('main'),
            E.type({
                'POINT': 'point',
                'LINESTRING': 'line',
                'POLYGON': 'polygon',
                'MULTIPOINT': 'point',
                'MULTILINESTRING': 'line',
                'MULTIPOLYGON': 'polygon'
            }[self.parent.geometry_type]),
            E.template('dummy.html'),
            E.projection("+init=epsg:3857"),
            E.extent(
                minx='-20037508.34',
                miny='-20037508.34',
                maxx='20037508.34',
                maxy='20037508.34'
            ),
            E.status('DEFAULT'),
        ]

        for e in reversed(layer_setup):
            elayer.insert(0, e)

        # PIXMAP и SVG маркеры: подставляем путь к файлу в SYMBOL cо значением TYPE 'PIXMAP' или 'SVG'
        for type_elem in emap.iterfind('./symbol/type'):
            if type_elem.text not in ('pixmap', 'svg'):
                continue

            symbol = type_elem.getparent()
            image = symbol.find('./image')

            try:
                marker = Marker.filter_by(
                    keyname=image.text
                ).one()

                image.text = env.file_storage.filename(marker.fileobj)

            except orm_exc.NoResultFound:
                # Если маркера не нашлось, то заменяем symbol на квадрат
                type_elem.text = 'vector'

                image.tag = 'points'
                image.text = '0 0 0 1 1 1 1 0 0 0'

                symbol.append(E.filled('true'))

        obj = Map().from_xml(emap)
        mapfile(obj, buf)

        mapobj = mapscript.fromstring(buf.getvalue().encode('utf-8'))

        layer = mapobj.getLayer(0)

        items = ','.join(fieldnames).encode('utf-8')
        layer.setProcessingKey('ITEMS', items)

        layer.setProcessingKey('APPROXIMATION_SCALE', 'full')
        layer.setProcessingKey('LABEL_NO_CLIP', 'true')

        for f in features:
            # У MapServer серьёзные проблемы с отрисовкой объектов,
            # содержащих дублирующиеся узлы, поэтому выкидываем их
            shape = mapscript.shapeObj.fromWKT(f.geom.simplify(0).wkt)

            shape.initValues(len(fieldnames))
            i = 0
            for fld in fieldnames:
                v = f.fields[fld]

                if v is None:
                    # TODO: Возможно есть более удачный способ
                    # передавать mapserver пустые значения, но
                    # пока он мне не известен
                    v = ""
                elif isinstance(v, unicode):
                    v = v.encode('utf-8')
                else:
                    v = repr(v)

                shape.setValue(i, v)
                i += 1

            layer.addFeature(shape)

        return mapobj


DataScope.read.require(
    DataScope.read,
    attr='parent', cls=MapserverStyle)


class _xml_attr(SP):

    def setter(self, srlzr, value):
        try:
            layer = etree.fromstring(value)
            relaxng = schema(Map)
            relaxng.assertValid(layer)

        except etree.XMLSyntaxError as e:
            raise ValidationError(e.message)

        except etree.DocumentInvalid as e:
            raise ValidationError(e.message)

        for cls in registry:
            if hasattr(cls, 'assert_valid'):
                tag = cls.name.lower()
                for el in layer.xpath('//%s' % tag):
                    try:
                        cls.assert_valid(el)
                    except Exception as e:
                        raise ValidationError("{0} within <{1}> tag".\
                            format(e.message, tag))

        SP.setter(self, srlzr, value)

PR_READ = ResourceScope.read
PR_UPDATE = ResourceScope.update


class StyleSerializer(Serializer):
    identity = MapserverStyle.identity
    resclass = MapserverStyle

    xml = _xml_attr(read=PR_READ, write=PR_UPDATE)
