from .util import RNG


class Directive:
    @classmethod
    def subclass(cls, name, single=True, **kwargs):
        class SubClass(cls):
            pass

        SubClass.name = name
        SubClass.single = single

        for k, v in kwargs.items():
            setattr(SubClass, k, v)

        SubClass.__name__ = SubClass.name

        return SubClass


class Keyword(Directive):
    """KEYWORD ..."""

    name = "KEYWORD"


class BlockDirective(Directive):
    """BLOCK ... END"""

    name = "BLOCK"


class PrimitiveKeyword(Keyword):
    """KEYWORD primitive"""

    def from_xml(self, e):
        self.value = self.primitive.from_xml(e)

    def to_mapfile(self, buf):
        buf.write("%s %s\n" % (self.name, self.value.to_mapfile()))

    @classmethod
    def element_schema(cls):
        return RNG.element(cls.primitive.xml_schema(), name=cls.name.lower())


class SimpleKeyword(Keyword):
    """KEYWORD value"""

    def from_xml(self, e):
        if isinstance(e, str):
            self.from_string(e)
        else:
            self.from_string(e.text)

    def to_mapfile(self, buf):
        buf.write("%s %s\n" % (self.name, self.to_string()))

    @classmethod
    def value_schema(cls):
        return RNG.text()

    @classmethod
    def element_schema(cls):
        return RNG.element(cls.value_schema(), name=cls.name.lower())


class CompositeDirective(BlockDirective):
    """
    BLOCK
        KEYWORD1 ...
        KEYWORD2 ...
        SUBBLOCK 1
            ...
        END
    END
    """

    def __init__(self):
        self.data = dict()
        self.registry = dict()
        for m in self.members:
            self.data[m.name] = None if m.single else list()
            self.directives = []
            self.registry[m.name] = m

    def from_xml(self, e):
        for c in e.iterfind("./"):
            name = c.tag.upper()
            cls = self.registry[name]

            mobj = cls()
            mobj.from_xml(c)
            self.directives.append(mobj)

            if cls.single:
                self.data[name] = mobj
            else:
                self.data[name].append(mobj)

        return self

    def to_mapfile(self, buf):
        buf.begin(self.name)

        for d in self.directives:
            d.to_mapfile(buf)

        buf.end()

    @classmethod
    def element_schema(self):
        i = RNG.interleave()
        e = RNG.element(i, name=self.name.lower())

        for m in self.members:
            if m.single:
                i.append(RNG.optional(m.element_schema()))
            else:
                i.append(RNG.zeroOrMore(m.element_schema()))

        return e
