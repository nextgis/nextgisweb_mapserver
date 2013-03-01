# -*- coding: utf-8 -*-
from random import choice
from StringIO import StringIO

import sqlalchemy as sa
import sqlalchemy.orm.exc as orm_exc

from lxml import etree
from lxml.builder import ElementMaker

from PIL import Image
import mapscript

from nextgisweb.geometry import box
from nextgisweb.feature_layer import IFeatureLayer, GEOM_TYPE

from .mapfile import Map, mapfile

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


def initialize(comp):
    file_storage = comp.env.file_storage
    marker_library = comp.env.marker_library

    Style = comp.env.style.Style

    @Style.registry.register
    class MapserverStyle(Style):
        __tablename__ = 'mapserver_style'

        identity = __tablename__
        cls_display_name = u"Стиль MapServer"

        style_id = sa.Column(sa.ForeignKey('style.id'), primary_key=True)
        xml = sa.Column(sa.Unicode, nullable=False)

        __mapper_args__ = dict(
            polymorphic_identity=identity,
        )

        @classmethod
        def is_layer_supported(cls, layer):
            return IFeatureLayer.providedBy(layer)

        @classmethod
        def default_style_xml(cls, layer):
            E = ElementMaker()

            style = E.style(
                E.color(dict(zip(
                    ('red', 'green', 'blue'), map(str, choice(_RNDCOLOR))
                ))),
                E.outlinecolor(red='64', green='64', blue='64'),
            )

            root = E.map(
                E.layer(
                    E('class', style)
                )
            )

            if layer.geometry_type == GEOM_TYPE.POINT:
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

        def render_image(self, extent, img_size, settings):
            padding = 128

            res_x = (extent[2] - extent[0]) / img_size[0]
            res_y = (extent[3] - extent[1]) / img_size[1]

            # Экстент с учетом запаса
            extended = (
                extent[0] - res_x * padding,
                extent[1] - res_y * padding,
                extent[2] + res_x * padding,
                extent[3] + res_y * padding,
            )

            # Размер изображения с учетом запаса
            render_size = (
                img_size[0] + 2 * padding,
                img_size[1] + 2 * padding
            )

            # Фрагмент изображения размера image_size
            target_box = (
                padding,
                padding,
                img_size[0] + padding,
                img_size[1] + padding
            )

            # Выбираем объекты по экстенту
            feature_query = self.layer.feature_query()
            feature_query.intersects(box(*extended, srid=self.layer.srs_id))
            feature_query.geom()
            features = feature_query()

            mapobj = self._mapobj(features)

            # Получаем картинку эмулируя WMS запрос
            req = mapscript.OWSRequest()
            req.setParameter("bbox", ','.join(map(str, extended)))
            req.setParameter("width", str(render_size[0]))
            req.setParameter("height", str(render_size[1]))
            req.setParameter("srs", 'EPSG:%d' % self.layer.srs_id)
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

        def _mapobj(self, features):
            # tmpf = NamedTemporaryFile(suffix='.map')
            # buf = codecs.open(tmpf.name, 'w', 'utf-8')
            buf = StringIO()

            fieldnames = map(lambda f: f.keyname, self.layer.fields)

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
                E.fontset(comp.settings['fontset']),
            ]

            for i in reversed(map_setup):
                emap.insert(0, i)

            # Настраиваем layer
            elayer = emap.find('./layer')

            layer_setup = [
                E.name('main'),
                E.type({
                    "POINT": 'point',
                    'LINESTRING': 'line',
                    'POLYGON': 'polygon'
                }[self.layer.geometry_type]),
                E.template('dummy.html'),
                E.projection("+init=epsg:3857"),
                E.extent(
                    minx='-20037508.34',
                    miny='-20037508.34',
                    maxx='20037508.34',
                    maxy='20037508.34'
                ),
            ]

            for e in reversed(layer_setup):
                elayer.insert(0, e)

            # SVG-маркеры: подставляем путь к файлу в SYMBOL c TYPE == 'SVG'
            for type_elem in emap.iterfind('./symbol/type'):
                if type_elem.text != 'svg':
                    continue

                symbol = type_elem.getparent()
                image = symbol.find('./image')

                try:
                    marker = marker_library.Marker.filter_by(
                        keyname=image.text
                    ).one()

                    image.text = file_storage.filename(marker.fileobj)

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
                shape = mapscript.shapeObj.fromWKT(f.geom.wkt)

                shape.initValues(len(fieldnames))
                i = 0
                for fld in fieldnames:
                    v = f.fields[fld]

                    if isinstance(v, unicode):
                        v = v.encode('utf-8')
                    else:
                        v = str(v)

                    shape.setValue(i, v)
                    i += 1

                layer.addFeature(shape)

            return mapobj

    comp.MapserverStyle = MapserverStyle
