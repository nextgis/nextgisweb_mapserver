# -*- coding: utf-8 -*-
import os.path
from lxml.etree import parse
from .. import qml, mapfile, extmapfile

QML_FILES = (
    # Точки
    'point_simple_marker',
    # Линии
    'line_highway_cycleway',
    'line_highway_ford',
    'line_highway_steps',
    'line_highway_trunk',
    'line_waterway_river',
    # Рендереры
    'renderer_single',
    'renderer_categorized',
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
