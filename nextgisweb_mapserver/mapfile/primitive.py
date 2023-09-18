import re

from .util import RNG


class Primitive(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def subclass(cls, **kwargs):
        class Subclass(cls):
            pass

        for k, v in kwargs.items():
            setattr(Subclass, k, v)

        return Subclass


class Integer(Primitive):
    @classmethod
    def isvalid(cls, t):
        return re.match(r"^[\+\-]{0,1}\d+$", t) is not None

    @classmethod
    def from_string(cls, t):
        return cls(int(t))

    def to_mapfile(self):
        return str(self.value)

    @classmethod
    def from_xml(cls, e):
        return cls(int(e.text))

    @classmethod
    def xml_schema(cls):
        return RNG.data(type="int")


class Double(Primitive):
    @classmethod
    def isvalid(cls, t):
        return re.match(r"^[\+\-]{0,1}\d+(\.\d+){0,1}$", t) is not None

    @classmethod
    def from_string(cls, t):
        return cls(float(t))

    def to_mapfile(self):
        return str(self.value)

    @classmethod
    def from_xml(cls, e):
        return cls(float(e.text))

    @classmethod
    def xml_schema(cls):
        return RNG.data(type="double")


class Boolean(Primitive):
    @classmethod
    def isvalid(cls, t):
        return re.match(r"^(true|false)$", t) is not None

    @classmethod
    def from_string(cls, t):
        if t == "true":
            return cls(True)

        elif t == "false":
            return cls(False)

    def to_mapfile(self):
        return "true" if self.value else "false"

    @classmethod
    def from_xml(cls, e):
        return cls(bool(e.text.lower()))

    @classmethod
    def xml_schema(cls):
        return RNG.choice(RNG.value("true"), RNG.value("false"))


class Enum(Primitive):
    @classmethod
    def isvalid(cls, t):
        return t in cls.choices

    @classmethod
    def from_string(cls, t):
        return cls(t)

    def to_mapfile(self):
        return self.value

    @classmethod
    def from_xml(cls, e):
        return cls(e.text)

    @classmethod
    def xml_schema(cls):
        return RNG.choice(*[RNG.value(o) for o in cls.choices])


class String(Primitive):
    @classmethod
    def isvalid(cls, t):
        return True

    @classmethod
    def from_string(cls, t):
        return cls(t)

    def to_mapfile(self):
        return '"%s"' % self.value

    @classmethod
    def from_xml(cls, e):
        return cls(e.text)

    @classmethod
    def xml_schema(cls):
        return RNG.text()


class Attribute(Primitive):
    def to_mapfile(self):
        # TODO: Escape!
        return "[%s]" % self.value

    @classmethod
    def from_xml(cls, e):
        return cls(e.text)

    @classmethod
    def xml_schema(cls):
        return RNG.text()


class Composite(Primitive):
    def to_mapfile(self):
        a = list()
        for k, p in self.items:
            a.append(self.value[k].to_mapfile())

        return " ".join(a)

    @classmethod
    def from_xml(cls, e):
        index = dict()
        for k, p in cls.items:
            index[k] = p

        value = dict()
        for a, v in e.attrib.items():
            value[a] = index[a].from_xml(RNG.value(v))

        return cls(value)

    @classmethod
    def xml_schema(cls):
        e = RNG.group()
        for k, p in cls.items:
            e.append(RNG.attribute(p.xml_schema(), name=k))

        return e
