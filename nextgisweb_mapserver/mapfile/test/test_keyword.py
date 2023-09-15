import pytest
from lxml.etree import RelaxNG, fromstring, tostring

from ..keyword import registry


@pytest.mark.parametrize("cls", registry)
def test_schema(cls):
    root = cls.element_schema()
    root.set("datatypeLibrary", "http://www.w3.org/2001/XMLSchema-datatypes")

    xml = tostring(root, pretty_print=True).decode("utf-8")
    RelaxNG(fromstring(xml))
