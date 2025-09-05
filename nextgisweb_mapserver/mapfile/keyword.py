from . import primitive as p
from .expressions import parser
from .grammar import BlockDirective, CompositeDirective, PrimitiveKeyword, SimpleKeyword
from .util import RNG

registry = list()


def register(cls):
    registry.append(cls)
    return cls


@register
class Integer(PrimitiveKeyword):
    primitive = p.Integer


@register
class Float(PrimitiveKeyword):
    primitive = p.Double


@register
class Boolean(PrimitiveKeyword):
    primitive = p.Boolean


@register
class String(PrimitiveKeyword):
    primitive = p.String


@register
class Attribute(PrimitiveKeyword):
    primitive = p.Attribute


@register
class Enum(PrimitiveKeyword):
    primitive = p.Enum.subclass(choices=("a", "b"))

    @classmethod
    def subclass(cls, name, choices=(), **kwargs):
        Subclass = PrimitiveKeyword.subclass(name, **kwargs)
        Subclass.primitive = p.Enum.subclass(choices=choices)
        return Subclass


@register
class Extent(PrimitiveKeyword):
    primitive = p.Composite.subclass(
        items=(
            ("minx", p.Double),
            ("miny", p.Double),
            ("maxx", p.Double),
            ("maxy", p.Double),
        )
    )


@register
class Color(PrimitiveKeyword):
    primitive = p.Composite.subclass(
        items=(
            ("red", p.Integer),
            ("green", p.Integer),
            ("blue", p.Integer),
        )
    )


@register
class Point(PrimitiveKeyword):
    primitive = p.Composite.subclass(items=(("x", p.Double), ("y", p.Double)))


Debug = register(Enum.subclass("Debug", choices="off|on|0|1|2|3|4|5".split("|")))


Switch = register(Enum.subclass("Switch", choices=("off", "on")))


@register
class Points(BlockDirective):
    name = "POINTS"

    def from_xml(self, e):
        self.value = map(float, e.text.split(" "))

    def to_mapfile(self, buf):
        buf.write("POINTS %s END\n" % " ".join(map(str, self.value)))

    @classmethod
    def element_schema(cls):
        return RNG.element(RNG.text(), name=cls.name.lower())


@register
class Pattern(BlockDirective):
    name = "PATTERN"

    def from_xml(self, e):
        self.value = map(float, e.text.split(" "))

    def to_mapfile(self, buf):
        buf.write("PATTERN %s END\n" % " ".join(map(str, self.value)))

    @classmethod
    def element_schema(cls):
        return RNG.element(RNG.text(), name=cls.name.lower())


@register
class Expression(PrimitiveKeyword):
    name = "EXPRESSION"

    def from_xml(self, e):
        self.value = e.text

    def to_mapfile(self, buf):
        buf.write("EXPRESSION %s\n" % self.value)

    @classmethod
    def element_schema(cls):
        return RNG.element(RNG.text(), name=cls.name.lower())

    @staticmethod
    def assert_valid(e):
        text = e.text
        parser.parse(text)


@register
class Style(CompositeDirective):
    class Angle(SimpleKeyword):
        def from_string(self, t):
            if t == "auto":
                self.value = "auto"
            else:
                self.value = float(t)

        def to_string(self):
            return str(self.value)

    name = "STYLE"
    members = (
        # ANGLE [double|attribute|auto]
        Angle.subclass("ANGLE"),
        # ANTIALIAS [true|false]
        Boolean.subclass("ANTIALIAS"),
        # BACKGROUNDCOLOR [r] [g] [b]
        Color.subclass("BACKGROUNDCOLOR"),
        # COLOR [r] [g] [b] | [attribute]
        Color.subclass("COLOR"),
        # GAP [double]
        Float.subclass("GAP"),
        # GEOMTRANSFORM bbox|end|labelpnt|labelpoly|
        #               start|vertices|<expression>
        # INITIALGAP [double]
        Float.subclass("INITIALGAP"),
        # LINECAP [butt|round|square]
        Enum.subclass("LINECAP", choices="butt|round|square".split("|")),
        # LINEJOIN [round|miter|bevel]
        Enum.subclass("LINEJOIN", choices="round|miter|bevel".split("|")),
        # LINEJOINMAXSIZE [int]
        Integer.subclass("LINEJOINMAXSIZE"),
        # MAXSCALEDENOM [double]
        Float.subclass("MAXSCALEDENOM"),
        # MAXSIZE [double]
        Float.subclass("MAXSIZE"),
        # MAXWIDTH [double]
        Float.subclass("MAXWIDTH"),
        # MINSCALEDENOM [double]
        Float.subclass("MINSCALEDENOM"),
        # MINSIZE [double]
        Float.subclass("MINSIZE"),
        # MINWIDTH [double]
        Float.subclass("MINWIDTH"),
        # OFFSET [x] [y]
        Point.subclass("OFFSET"),
        # OPACITY [integer|attribute]
        Integer.subclass("OPACITY"),
        # OUTLINECOLOR [r] [g] [b] | [attribute]
        Color.subclass("OUTLINECOLOR"),
        # OUTLINEWIDTH [double|attribute]
        Float.subclass("OUTLINEWIDTH"),
        # PATTERN [double on] [double off] [double on] [double off] ... END
        Pattern.subclass("PATTERN"),
        # POLAROFFSET [double|attribute] [double|attribute]
        # SIZE [double|attribute]
        Float.subclass("SIZE"),
        # SYMBOL [integer|string|filename|url|attribute]
        String.subclass("SYMBOL", single=False),
        # WIDTH [double|attribute]
        Float.subclass("WIDTH"),
    )


@register
class Label(CompositeDirective):
    @register
    class Style(CompositeDirective):
        name = "STYLE"
        members = (
            Enum.subclass("GEOMTRANSFORM", choices=("labelpoly", "labelpnt")),
            Color.subclass("COLOR"),
        )

    name = "LABEL"
    members = (
        # ALIGN [left|center|right]
        Enum.subclass("ALIGN", choices=("left", "center", "right")),
        # ANGLE [double|auto|auto2|follow|attribute]
        Enum.subclass("ANGLE", choices=("auto", "follow")),
        # ANTIALIAS [true|false]
        Boolean.subclass("ANTIALIAS"),
        # BUFFER [integer]
        Integer.subclass("BUFFER"),
        # COLOR [r] [g] [b] | [attribute]
        Color.subclass("COLOR"),
        # ENCODING [string]
        String.subclass("ENCODING"),
        # EXPRESSION [string]
        Expression.subclass("EXPRESSION"),
        # FONT [name|attribute]
        String.subclass("FONT"),
        # FORCE [true|false]
        Boolean.subclass("FORCE"),
        # MAXLENGTH [integer]
        Integer.subclass("MAXLENGTH"),
        # MAXOVERLAPANGLE [double]
        Float.subclass("MAXOVERLAPANGLE"),
        # MAXSCALEDENOM [double]
        Float.subclass("MAXSCALEDENOM"),
        # MAXSIZE [double]
        Float.subclass("MAXSIZE"),
        # MINDISTANCE [integer]
        Integer.subclass("MINDISTANCE"),
        # MINFEATURESIZE [integer]|[auto]
        Integer.subclass("MINFEATURESIZE"),
        # MINSCALEDENOM [double]
        Float.subclass("MINSCALEDENOM"),
        # MINSIZE [double]
        Float.subclass("MINSIZE"),
        # OFFSET [x] [y]
        Point.subclass("OFFSET"),
        # OUTLINECOLOR [r] [g] [b] | [attribute]
        Color.subclass("OUTLINECOLOR"),
        # OUTLINEWIDTH [integer]
        Integer.subclass("OUTLINEWIDTH"),
        # PARTIALS [true|false]
        Boolean.subclass("PARTIALS"),
        # POSITION [ul|uc|ur|cl|cc|cr|ll|lc|lr|auto]
        Enum.subclass("POSITION", choices="ul|uc|ur|cl|cc|cr|ll|lc|lr|auto".split("|")),
        # PRIORITY [integer]|[item_name]|[attribute]
        # REPEATDISTANCE [integer]
        Integer.subclass("REPEATDISTANCE"),
        # SHADOWCOLOR [r] [g] [b]
        Color.subclass("SHADOWCOLOR"),
        # SHADOWSIZE [x][y]|[attribute][attribute]
        #            | [x][attribute]|[attribute][y]
        # SIZE [double]|[tiny|small|medium|large|giant]|[attribute]
        Float.subclass("SIZE"),
        # STYLE
        Style.subclass("STYLE"),
        # TEXT [string|expression]
        # TYPE [bitmap|truetype]
        Enum.subclass("TYPE", choices=("bitmap", "truetype")),
        # # WRAP [character]
    )


@register
class Class(CompositeDirective):
    name = "CLASS"
    members = (
        # DEBUG [on|off]
        Debug.subclass("DEBUG"),
        # EXPRESSION [string]
        Expression.subclass("EXPRESSION"),
        # GROUP [string]
        String.subclass("GROUP"),
        # KEYIMAGE [filename]
        String.subclass("KEYIMAGE"),
        # LABEL
        Label.subclass("LABEL", single=False),
        # LEADER
        # MAXSCALEDENOM [double]
        Float.subclass("MAXSCALEDENOM"),
        # MINSCALEDENOM [double]
        Float.subclass("MINSCALEDENOM"),
        # NAME [string]
        String.subclass("NAME"),
        # STATUS [on|off]
        Switch.subclass("STATUS"),
        # STYLE
        Style.subclass("STYLE", single=False),
        # SYMBOL [integer|string|filename]
        # TEMPLATE [filename]
        String.subclass("TEMPLATE"),
        # TEXT [string|expression]
        # VALIDATION
    )


@register
class Projection(BlockDirective):
    name = "PROJECTION"

    def from_xml(self, e):
        self.value = e.text

    def to_mapfile(self, buf):
        buf.begin(self.name)
        for s in self.value.split(" "):
            buf.write('"%s"\n' % s)
        buf.end()

    @classmethod
    def element_schema(self):
        return RNG.element(RNG.text(), name=self.name.lower())


@register
class Metadata(BlockDirective):
    name = "METADATA"

    def from_xml(self, e):
        self.value = dict()
        for pr in e.iterfind("./item"):
            self.value[pr.attrib["key"]] = pr.attrib["value"]

    def to_mapfile(self, buf):
        buf.begin(self.name)
        for k, v in self.value.items():
            buf.write('"%s" "%s"\n' % (k, v))
        buf.end()

    @classmethod
    def element_schema(cls):
        return RNG.element(
            RNG.oneOrMore(
                RNG.element(
                    RNG.attribute(RNG.text(), name="key"),
                    RNG.attribute(RNG.text(), name="value"),
                    name="item",
                )
            ),
            name=cls.name.lower(),
        )


@register
class Feature(CompositeDirective):
    name = "FEATURE"
    members = (
        # POINTS
        Points.subclass("POINTS"),
        # ITEMS
        String.subclass("ITEMS"),
        # TEXT [string]
        # WKT [string]
        String.subclass("WKT"),
    )


@register
class Cluster(CompositeDirective):
    name = "CLUSTER"
    members = (
        # MAXDISTANCE [double]
        Float.subclass("MAXDISTANCE"),
        # REGION [string]
        Enum.subclass("REGION", choices=('"rectangle"', '"ellipse"')),
        # BUFFER [double]
        Float.subclass("BUFFER"),
        # GROUP [string]
        String.subclass("GROUP"),
        # FILTER [string]
        String.subclass("FILTER"),
    )


@register
class Layer(CompositeDirective):
    name = "LAYER"
    members = (
        # CLASS
        Class.subclass("CLASS", single=False),
        # CLASSGROUP [string]
        String.subclass("CLASSGROUP"),
        # CLASSITEM [string]
        String.subclass("CLASSITEM"),
        # CLUSTER
        Cluster.subclass("CLUSTER"),
        # CONNECTION [string]
        String.subclass("CONNECTION"),
        # CONNECTIONTYPE local|ogr|oraclespatial|plugin|
        #                postgis|sde|union|uvraster|wfs|wms]
        Enum.subclass(
            "CONNECTIONTYPE",
            choices=("local|ogr|oraclespatial|plugin|postgis|sde|union|uvraster|wfs|wms").split(
                "|"
            ),
        ),
        # DATA [filename] |
        #      [sde parameters] |
        #      [postgis table/column] |
        #      [oracle table/column]
        # DEBUG [off|on|0|1|2|3|4|5]
        Debug.subclass("DEBUG"),
        # EXTENT [minx] [miny] [maxx] [maxy]
        Extent.subclass("EXTENT"),
        # FEATURE
        Feature.subclass("FEATURE", single=False),
        # FILTER [string]
        String.subclass("FILTER"),
        # FILTERITEM [attribute]
        # FOOTER [filename]
        String.subclass("FOOTER"),
        # GRID
        # GROUP [name]
        String.subclass("GROUP"),
        # HEADER [filename]
        String.subclass("HEADER"),
        # JOIN
        # LABELCACHE [on|off]
        Switch.subclass("LABELCACHE"),
        # LABELITEM [attribute]
        String.subclass("LABELITEM"),
        # LABELMAXSCALEDENOM [double]
        Float.subclass("LABELMAXSCALEDENOM"),
        # LABELMINSCALEDENOM [double]
        Float.subclass("LABELMINSCALEDENOM"),
        # LABELREQUIRES [expression]
        # MASK [layername]
        String.subclass("MASK"),
        # MAXFEATURES [integer]
        Integer.subclass("MAXFEATURES"),
        # MAXGEOWIDTH [double]
        Float.subclass("MAXGEOWIDTH"),
        # MAXSCALEDENOM [double]
        Float.subclass("MAXSCALEDENOM"),
        # METADATA
        Metadata.subclass("METADATA"),
        # MINGEOWIDTH [double]
        Float.subclass("MINGEOWIDTH"),
        # MINSCALEDENOM [double]
        Float.subclass("MINSCALEDENOM"),
        # NAME [string]
        # NAME tag is not allowed here because not compatible
        # with an internally used 'main' layer name, but
        # it is impossible to comment it now.
        String.subclass("NAME"),
        # OFFSITE [r] [g] [b]
        Color.subclass("OFFSITE"),
        # OPACITY [integer|alpha]
        Integer.subclass("OPACITY"),
        # PLUGIN [filename]
        String.subclass("PLUGIN"),
        # POSTLABELCACHE [true|false]
        Boolean.subclass("POSTLABELCACHE"),
        # PROCESSING [string]
        String.subclass("PROCESSING", single=False),
        # PROJECTION
        Projection.subclass("PROJECTION"),
        # REQUIRES [expression]
        # SIZEUNITS [feet|inches|kilometers|meters|miles|nauticalmiles|pixels]
        Enum.subclass(
            "SIZEUNITS",
            choices=("feet|inches|kilometers|meters|miles|nauticalmiles|pixels").split("|"),
        ),
        # STATUS [on|off|default]
        Enum.subclass("STATUS", choices="on|off|default".split("|")),
        # STYLEITEM [<attribute>|auto]
        String.subclass("STYLEITEM"),
        # SYMBOLSCALEDENOM [double]
        Float.subclass("SYMBOLSCALEDENOM"),
        # TEMPLATE [file|url]
        String.subclass("TEMPLATE"),
        # TILEINDEX [filename|layername]
        String.subclass("TILEINDEX"),
        # TILEITEM [attribute]
        # TOLERANCE [double]
        Float.subclass("TOLERANCE"),
        # TOLERANCEUNITS pixels|feet|inches|kilometers|
        #                meters|miles|nauticalmiles|dd
        Enum.subclass(
            "TOLERANCEUNITS",
            choices=("pixels|feet|inches|kilometers|meters|miles|nauticalmiles|dd").split("|"),
        ),
        # TRANSFORM [true|false ul|uc|ur|lc|cc|lr|ll|lc|lr]
        # TYPE [chart|circle|line|point|polygon|raster|query]
        Enum.subclass("TYPE", choices="chart|circle|line|point|polygon|raster|query".split("|")),
        # UNITS dd|feet|inches|kilometers|meters|miles|
        #       nauticalmiles|percentages|pixels
        Enum.subclass(
            "UNITS",
            choices=(
                "dd|feet|inches|kilometers|meters|miles|nauticalmiles|percentages|pixels"
            ).split("|"),
        ),
        # VALIDATION
    )


@register
class Web(CompositeDirective):
    name = "WEB"
    members = (
        # BROWSEFORMAT [mime-type]
        String.subclass("BROWSEFORMAT"),
        # EMPTY [url]
        String.subclass("EMPTY"),
        # ERROR [url]
        String.subclass("ERROR"),
        # FOOTER [filename]
        String.subclass("FOOTER"),
        # HEADER [filename]
        String.subclass("HEADER"),
        # IMAGEPATH [path]
        String.subclass("IMAGEPATH"),
        # IMAGEURL [path]
        String.subclass("IMAGEURL"),
        # LEGENDFORMAT [mime-type]
        String.subclass("LEGENDFORMAT"),
        # MAXSCALEDENOM [double]
        String.subclass("MAXSCALEDENOM"),
        # MAXTEMPLATE [file|url]
        String.subclass("MAXTEMPLATE"),
        # METADATA
        Metadata.subclass("METADATA"),
        # MINSCALEDENOM [double]
        String.subclass("MINSCALEDENOM"),
        # QUERYFORMAT [mime-type]
        String.subclass("QUERYFORMAT"),
        # TEMPLATE [filename|url]
        String.subclass("TEMPLATE"),
        # TEMPPATH
        String.subclass("TEMPPATH"),
        # VALIDATION
    )


@register
class OutputFormat(CompositeDirective):
    name = "OUTPUTFORMAT"
    members = (
        # DRIVER [name]
        String.subclass("DRIVER"),
        # EXTENSION [type]
        String.subclass("EXTENSION"),
        # FORMATOPTION [option]
        String.subclass("FORMATOPTION", single=False),
        # IMAGEMODE [PC256/RGB/RGBA/INT16/FLOAT32/FEATURE]
        Enum.subclass("IMAGEMODE", choices="PC256|RGB|RGBA|INT16|FLOAT32|FEATURE".split("|")),
        # MIMETYPE [type]
        String.subclass("MIMETYPE"),
        # NAME [name]
        String.subclass("NAME"),
    )


@register
class Symbol(CompositeDirective):
    name = "SYMBOL"
    members = (
        # ANCHORPOINT [x] [y]
        Point.subclass("ANCHORPOINT"),
        # ANTIALIAS [true|false]
        Boolean.subclass("ANTIALIAS"),
        # CHARACTER [char]
        String.subclass("CHARACTER"),
        # FILLED [true|false]
        Boolean.subclass("FILLED"),
        # FONT [string]
        String.subclass("FONT"),
        # IMAGE [string]
        String.subclass("IMAGE"),
        # NAME [string]
        String.subclass("NAME"),
        # POINTS [x y] [x y] ... END
        Points.subclass("POINTS"),
        # TRANSPARENT [integer]
        Integer.subclass("TRANSPARENT"),
        # TYPE [ellipse|hatch|pixmap|svg|truetype|vector]
        Enum.subclass("TYPE", choices="ellipse|hatch|pixmap|svg|truetype|vector".split("|")),
    )


@register
class Legend(CompositeDirective):
    name = "LEGEND"
    members = (
        # IMAGECOLOR [r] [g] [b]
        # KEYSIZE [x] [y]
        Point.subclass("KEYSIZE"),
        # KEYSPACING [x] [y]
        Point.subclass("KEYSPACING"),
        # LABEL
        Label.subclass("LABEL"),
        # OUTLINECOLOR [r] [g] [b]
        Color.subclass("OUTLINECOLOR"),
        # POSITION [ul|uc|ur|ll|lc|lr]
        # POSTLABELCACHE [true|false]
        # STATUS [on|off|embed]
        # TEMPLATE [filename]
    )


@register
class Map(CompositeDirective):
    name = "MAP"

    class Size(SimpleKeyword):
        def from_xml(self, e):
            self.value = tuple(map(int, map(e.get, ("width", "height"))))

        def to_string(self):
            return "%d %d" % self.value

        @classmethod
        def element_schema(cls):
            e = RNG.element(name=cls.name.lower())
            for a in ("width", "height"):
                e.append(RNG.attribute(RNG.data(type="int"), name=a))
            return e

    members = (
        # ANGLE [double]
        Float.subclass("ANGLE"),
        # CONFIG [key] [value]
        # DATAPATTERN [regular expression]
        # DEBUG [off|on|0|1|2|3|4|5]
        Debug.subclass("DEBUG"),
        # DEFRESOLUTION [integer]
        Integer.subclass("DEFRESOLUTION"),
        # EXTENT [minx] [miny] [maxx] [maxy]
        Extent.subclass("EXTENT"),
        # FONTSET [filename]
        String.subclass("FONTSET"),
        # IMAGECOLOR [r] [g] [b]
        Color.subclass("IMAGECOLOR"),
        # IMAGETYPE [jpeg|pdf|png|svg|...|userdefined]
        Enum.subclass("IMAGETYPE", choices="jpeg|pdf|png|svg".split("|")),
        # LAYER
        Layer.subclass("LAYER", single=False),
        # LEGEND
        Legend.subclass("LEGEND"),
        # MAXSIZE [integer]
        Integer.subclass("MAXSIZE"),
        # NAME [name]
        String.subclass("NAME"),
        # OUTPUTFORMAT
        OutputFormat.subclass("OUTPUTFORMAT"),
        # PROJECTION
        Projection.subclass("PROJECTION"),
        # QUERYMAP
        # REFERENCE
        # RESOLUTION [integer]
        Integer.subclass("RESOLUTION"),
        # SCALEDENOM [double]
        Float.subclass("SCALEDENOM"),
        # SCALEBAR
        # SHAPEPATH [filename]
        String.subclass("SHAPEPATH"),
        # SIZE [x] [y]
        Size.subclass("SIZE"),
        # STATUS [on|off]
        Switch.subclass("STATUS"),
        # SYMBOLSET [filename]
        String.subclass("SYMBOLSET"),
        # SYMBOL
        Symbol.subclass("SYMBOL", single=False),
        # TEMPLATEPATTERN [regular expression]
        # UNITS dd|feet|inches|kilometers|
        #       meters|miles|nauticalmiles
        Enum.subclass(
            "UNITS", choices=("dd|feet|inches|kilometers|meters|miles|nauticalmiles").split("|")
        ),
        # WEB
        Web.subclass("WEB"),
    )
