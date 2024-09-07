import datetime
from io import BytesIO, StringIO
from pkg_resources import resource_filename
from random import choice

import mapscript
import sqlalchemy as sa
from lxml import etree
from lxml.builder import ElementMaker
from PIL import Image
from zope.interface import implementer

from nextgisweb.env import Base, env, gettext
from nextgisweb.lib.geometry import Geometry

from nextgisweb.feature_layer import GEOM_TYPE, IFeatureLayer
from nextgisweb.render import (
    IExtentRenderRequest,
    ILegendableStyle,
    IRenderableStyle,
    ITileRenderRequest,
)
from nextgisweb.resource import DataScope, Resource, ResourceScope, SColumn, Serializer
from nextgisweb.resource.exception import ValidationError

from .mapfile import Map, mapfile, registry, schema

# ColorBrewer
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


@implementer(IExtentRenderRequest, ITileRenderRequest)
class RenderRequest(object):
    def __init__(self, style, srs, cond):
        self.style = style
        self.srs = srs
        self.cond = cond

    def render_extent(self, extent, size):
        return self.style.render_image(self.srs, extent, size, self.cond)

    def render_tile(self, tile, size):
        extent = self.srs.tile_extent(tile)
        return self.style.render_image(self.srs, extent, (size, size), self.cond, padding=size / 2)


@implementer((IRenderableStyle, ILegendableStyle))
class MapserverStyle(Base, Resource):
    identity = "mapserver_style"
    cls_display_name = gettext("MapServer style")

    __scope__ = DataScope

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
    def default_style_xml(cls, layer, color=None):
        if color is None:
            color = choice(_RNDCOLOR)

        E = ElementMaker()

        style = E.style(
            E.color(dict(zip(("red", "green", "blue"), map(str, color)))),
            E.outlinecolor(red="64", green="64", blue="64"),
        )

        legend = E.legend(
            E.keysize(x="15", y="15"), E.label(E.size("12"), E.type("truetype"), E.font("regular"))
        )

        root = E.map(E.layer(E("class", style)), legend)

        if layer.geometry_type in (
            GEOM_TYPE.POINT,
            GEOM_TYPE.MULTIPOINT,
            GEOM_TYPE.POINTZ,
            GEOM_TYPE.MULTIPOINTZ,
        ):
            symbol = E.symbol(
                E.type("ellipse"),
                E.name("circle"),
                E.points("1 1"),
                E.filled("true"),
            )

            root.insert(0, symbol)

            style.append(E.symbol("circle"))
            style.append(E.size("6"))

        return etree.tostring(root, pretty_print=True, encoding="unicode")

    def render_image(self, srs, extent, size, cond, padding=0):
        res_x = (extent[2] - extent[0]) / size[0]
        res_y = (extent[3] - extent[1]) / size[1]

        extended = (
            extent[0] - res_x * padding,
            extent[1] - res_y * padding,
            extent[2] + res_x * padding,
            extent[3] + res_y * padding,
        )

        render_size = (size[0] + 2 * padding, size[1] + 2 * padding)

        target_box = (padding, padding, size[0] + padding, size[1] + padding)

        feature_query = self.parent.feature_query()

        if cond is not None:
            feature_query.filter_by(**cond)

        feature_query.srs(srs)

        feature_query.intersects(Geometry.from_box(*extended, srid=srs.id))
        feature_query.geom()
        features = list(feature_query())

        if len(features) == 0:
            return None

        mapobj = self._mapobj(features)

        req = mapscript.OWSRequest()
        req.setParameter("bbox", ",".join(map(str, extended if padding else extent)))
        req.setParameter("width", str(render_size[0]))
        req.setParameter("height", str(render_size[1]))
        req.setParameter("srs", "EPSG:%d" % self.parent.srs_id)
        req.setParameter("format", "image/png")
        req.setParameter("layers", "main")
        req.setParameter("request", "GetMap")
        req.setParameter("transparent", "TRUE")

        mapobj.loadOWSParameters(req)
        gdimg = mapobj.draw()

        buf = BytesIO()
        buf.write(gdimg.getBytes())
        buf.seek(0)

        img = Image.open(buf)

        return img.crop(target_box)

    def render_legend(self):
        mapobj = self._mapobj(features=[])
        gdimg = mapobj.drawLegend()

        buf = BytesIO()
        buf.write(gdimg.getBytes())
        buf.seek(0)

        return buf

    def _mapobj(self, features):
        # tmpf = NamedTemporaryFile(suffix='.map')
        # buf = codecs.open(tmpf.name, 'w', 'utf-8')
        buf = StringIO()

        fieldnames = [f.keyname for f in self.parent.fields]

        E = ElementMaker()

        emap = etree.fromstring(self.xml)

        map_setup = [
            E.size(width="800", height="600"),
            E.maxsize("4096"),
            E.imagecolor(red="255", green="255", blue="255"),
            E.imagetype("PNG"),
            E.outputformat(
                E.name("png"),
                E.extension("png"),
                E.mimetype("image/png"),
                E.driver("AGG/PNG"),
                E.imagemode("RGBA"),
                E.formatoption("INTERLACE=OFF"),
            ),
            E.web(
                E.metadata(
                    E.item(key="wms_onlineresource", value="http://localhost/"),
                    E.item(key="wfs_onlineresource", value="http://localhost/"),
                    E.item(key="ows_title", value="nextgisweb"),
                    E.item(key="wms_enable_request", value="*"),
                    E.item(key="wms_srs", value="EPSG:3857"),
                )
            ),
            E.extent(minx="-180", miny="-90", maxx="180", maxy="90"),
            E.projection("+init=epsg:4326"),
            E.fontset(env.mapserver.options["fontset"]),
            E.symbolset(resource_filename("nextgisweb_mapserver", "symbolset")),
        ]

        for i in reversed(map_setup):
            emap.insert(0, i)

        elayer = emap.find("./layer")

        layer_setup = [
            E.name("main"),
            E.type(
                {
                    GEOM_TYPE.POINT: "point",
                    GEOM_TYPE.LINESTRING: "line",
                    GEOM_TYPE.POLYGON: "polygon",
                    GEOM_TYPE.MULTIPOINT: "point",
                    GEOM_TYPE.MULTILINESTRING: "line",
                    GEOM_TYPE.MULTIPOLYGON: "polygon",
                    GEOM_TYPE.POINTZ: "point",
                    GEOM_TYPE.LINESTRINGZ: "line",
                    GEOM_TYPE.POLYGONZ: "polygon",
                    GEOM_TYPE.MULTIPOINTZ: "point",
                    GEOM_TYPE.MULTILINESTRINGZ: "line",
                    GEOM_TYPE.MULTIPOLYGONZ: "polygon",
                }[self.parent.geometry_type]
            ),
            E.template("dummy.html"),
            E.projection("+init=epsg:3857"),
            E.extent(
                minx="-20037508.34", miny="-20037508.34", maxx="20037508.34", maxy="20037508.34"
            ),
            E.status("DEFAULT"),
        ]

        for e in reversed(layer_setup):
            elayer.insert(0, e)

        # PIXMAP & SVG markers: replace to rectangle
        for type_elem in emap.iterfind("./symbol/type"):
            if type_elem.text not in ("pixmap", "svg"):
                continue

            symbol = type_elem.getparent()
            image = symbol.find("./image")

            # TODO: Set path to SVG marker library
            # image.text = ...

            type_elem.text = "vector"
            image.tag = "points"
            image.text = "0 0 0 1 1 1 1 0 0 0"
            symbol.append(E.filled("true"))

        obj = Map().from_xml(emap)
        mapfile(obj, buf)

        val = buf.getvalue()
        mapobj = mapscript.fromstring(val)

        layer = mapobj.getLayer(0)

        items = ",".join(fieldnames)
        layer.setProcessingKey("ITEMS", items)

        layer.setProcessingKey("APPROXIMATION_SCALE", "full")
        layer.setProcessingKey("LABEL_NO_CLIP", "true")

        for f in features:
            # MapServer has problems while rendering 3D geometries and
            # geometries with duplicate points.
            ogr_geom = f.geom.ogr
            ogr_geom.Set3D(False)
            ogr_geom.Simplify(0)
            shape = mapscript.shapeObj.fromWKT(ogr_geom.ExportToIsoWkt())

            shape.initValues(len(fieldnames))
            for i, fld in enumerate(fieldnames, start=0):
                v = f.fields[fld]

                if v is None:
                    # TODO: There is no other way to pass empty values
                    v = ""
                elif isinstance(v, str):
                    pass
                elif isinstance(v, bytes):
                    v = v.decode("utf-8")
                elif isinstance(v, datetime.date):
                    v = v.strftime(r"%Y-%m-%dT%H:%M:%S")
                else:
                    v = repr(v)

                shape.setValue(i, v)

            layer.addFeature(shape)

        return mapobj


DataScope.read.require(DataScope.read, attr="parent", cls=MapserverStyle)


class XmlAttr(SColumn, apitype=True):
    def get(self, srlzr: Serializer) -> str:
        return super().get(srlzr)

    def set(self, srlzr: Serializer, value: str, *, create: bool):
        try:
            layer = etree.fromstring(value)
            relaxng = schema(Map)
            relaxng.assertValid(layer)

        except etree.XMLSyntaxError as e:
            raise ValidationError(gettext("XML syntax error: %s") % str(e))

        except etree.DocumentInvalid as e:
            raise ValidationError(gettext("XML schema error: %s") % str(e))

        for cls in registry:
            if hasattr(cls, "assert_valid"):
                tag = cls.name.lower()
                for el in layer.xpath("//%s" % tag):
                    try:
                        cls.assert_valid(el)
                    except Exception as e:
                        raise ValidationError("{0} within <{1}> tag".format(str(e), tag))

        super().set(srlzr, value, create=create)


class MapserverStyleSerializer(Serializer, resource=MapserverStyle):
    xml = XmlAttr(read=ResourceScope.read, write=ResourceScope.update)
