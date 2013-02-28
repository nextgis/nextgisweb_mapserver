# -*- coding: utf-8 -*-
import os.path
from lxml.etree import parse
from .. import qml, mapfile, extmapfile

QML_FILES = (
    'point_single_symbol',
    'point_categorized_symbol',
)


def warn(e, t, msg):
    print 'WARN: ' + msg


def _transform(filename):
    filename = os.path.join(
        os.path.split(__file__)[0],
        'testdata',
        filename + '.qml'
    )
    elem = parse(filename).getroot()
    return qml.transform(elem, warn=warn)


def _validate(filename):
    schema = mapfile.schema(extmapfile.Map)
    schema.assertValid(_transform(filename))


def test_transform():
    for fn in QML_FILES:
        yield (_transform, fn)


def test_validate():
    for fn in QML_FILES:
        yield (_validate, fn)
