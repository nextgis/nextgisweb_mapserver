# -*- coding: utf-8 -*-
from random import choice
import codecs
from StringIO import StringIO
from tempfile import NamedTemporaryFile

import sqlalchemy as sa
import sqlalchemy.orm.exc as orm_exc

from lxml import etree
from lxml.builder import ElementMaker

from PIL import Image
import mapscript

from nextgisweb.geometry import box
from nextgisweb.feature_layer import IFeatureLayer, GEOM_TYPE

from .xmlmapfile import element_to_mapfile

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
                    E.points('1 1'),
                    E.filled('true'),
                )

                symbol.set('name', 'circle')
                symbol.set('type', 'ellipse')

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

            # Создаем объект mapscript из строки
            tmapfile = NamedTemporaryFile(suffix='.map')
            mapfile = codecs.open(tmapfile.name, 'w', 'utf-8')
            self._mapfile(features, mapfile)
            mapfile.flush()

            mapobj = mapscript.mapObj(mapfile.name)

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

        def _mapfile(self, features, buf):
            fieldnames = map(lambda f: f.keyname, self.layer.fields)

            E = ElementMaker()

            # Настраиваем map
            emap = etree.fromstring(self.xml)

            map_setup = [
                E.size('800 600'),
                E.maxSize('4096'),
                E.imageColor(red='255', green='255', blue='255'),
                E.imageType('PNG'),
                E.OutputFormat(
                    E.name('png'),
                    E.extension('png'),
                    E.mimeType('image/png'),
                    E.driver('AGG/PNG'),
                    E.imageMode('RGBA'),
                    E.formatOption('INTERLACE=OFF')
                ),
                E.Web(
                    E.MetaData(
                        E.wms_onlineresource('http://localhost/'),
                        E.wfs_onlineresource('http://localhost/'),
                        E.ows_title('nextgisweb'),
                        E.wms_enable_request('*'),
                        E.wms_srs('EPSG:3857')
                    )
                ),
                E.extent('-180 -90 180 90'),
                E.projection(epsg='4326'),
                E.fontset(comp.settings['fontset']),
            ]

            for i in reversed(map_setup):
                emap.insert(0, i)

            # Настраиваем layer
            elayer = emap.find('./layer')

            layer_setup = [
                E.name('main'),
                E.processing('ITEMS=%s' % ','.join(fieldnames)),
                E.processing('APPROXIMATION_SCALE=FULL'),
                E.processing('LABEL_NO_CLIP=True'),
                E.type({
                    "POINT": 'point',
                    'LINESTRING': 'line',
                    'POLYGON': 'polygon'
                }[self.layer.geometry_type]),
                E.template('dummy.html'),
                E.projection(epsg="3857"),
                E.extent('-20037508.34 -20037508.34 20037508.34 20037508.34'),
            ]

            for e in reversed(layer_setup):
                elayer.insert(0, e)

            # SVG-маркеры: находим элементы <symbol type="svg">
            # и заменяем элемент <marker>keyname</marker> на
            # <image>filename</image>
            for esymbol in emap.iterfind('./symbol'):
                if esymbol.get('type', None) != 'svg':
                    continue

                emarker = esymbol.find('./marker')

                try:
                    marker = marker_library.Marker.filter_by(
                        keyname=emarker.text
                    ).one()

                    emarker.text = file_storage.filename(marker.fileobj)
                    emarker.tag = 'image'

                except orm_exc.NoResultFound:
                    # Если маркера не нашлось, то заменяем symbol на окружность
                    esymbol.set('type', 'ellipse')
                    emarker.tag = 'points'
                    emarker.text = '1 1'

            # Добавляем данные в виде элементов feature в конец слоя
            for f in features:
                elayer.append(E.feature(
                    E.wkt(f.geom.wkt),
                    E.items(
                        ';'.join(
                            # TODO: Разобратся с escape
                            [unicode(f.fields[fld]) for fld in fieldnames]
                        )
                    )
                ))

            # Пишем получившийся mapfile в буфер
            element_to_mapfile(emap, buf)

    comp.MapserverStyle = MapserverStyle