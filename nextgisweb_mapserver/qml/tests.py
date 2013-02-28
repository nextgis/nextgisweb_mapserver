# -*- coding: utf-8 -*-
import os.path
from lxml.etree import parse
from .. import qml, mapfile, extmapfile

QML_FILES = (
    # Точка
    'point_simple_marker',
    # Линия
    'line_highway_cycleway',
    'line_highway_ford',
    'line_highway_steps',
    'line_highway_trunk',
    'line_waterway_river',
    # Полигон
    'polygon_simple_fill_bdiagonal',
    'polygon_simple_fill_cross',
    'polygon_simple_fill_dense1',
    'polygon_simple_fill_dense2',
    'polygon_simple_fill_dense3',
    'polygon_simple_fill_dense4',
    'polygon_simple_fill_dense5',
    'polygon_simple_fill_dense6',
    'polygon_simple_fill_dense7',
    'polygon_simple_fill_diagonalx',
    'polygon_simple_fill_fdiagonal',
    'polygon_simple_fill_horizontal',
    'polygon_simple_fill_opacity',
    'polygon_simple_fill_outline_dash',
    'polygon_simple_fill_outline_empty',
    'polygon_simple_fill_solid',
    'polygon_simple_fill_vertical',
    # Рендерер
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
