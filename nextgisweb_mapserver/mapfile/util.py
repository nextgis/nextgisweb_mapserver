from lxml.builder import ElementMaker
from lxml.etree import RelaxNG, fromstring, tostring

E = ElementMaker()
RNG = ElementMaker(namespace="http://relaxng.org/ns/structure/1.0")


class MapfileBuffer:
    def __init__(self, buf, indent=0):
        self._buf = buf
        self._indent = indent
        self._newline = True

    def write(self, s, indent=False, dedent=False):
        if dedent:
            self._indent -= 1

        self._buf.write((("  " * self._indent) if self._newline else "") + s)

        if indent:
            self._indent += 1

        self._newline = s[-1] == "\n"

    def newline(self):
        self.write("\n")

    def begin(self, block):
        self.write(block + "\n", indent=True)

    def end(self):
        self.write("END" + "\n", dedent=True)


def schema(cls):
    root = cls.element_schema()
    root.set("datatypeLibrary", "http://www.w3.org/2001/XMLSchema-datatypes")
    return RelaxNG(fromstring(tostring(root)))


def mapfile(obj, buf):
    buf = MapfileBuffer(buf)
    obj.to_mapfile(buf)
