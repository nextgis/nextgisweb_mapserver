from pathlib import Path

import pytest
import transaction

from nextgisweb.spatial_ref_sys import SRS
from nextgisweb.vector_layer import VectorLayer

from ..model import MapserverStyle

pytestmark = pytest.mark.usefixtures("ngw_resource_defaults")

color = (200, 0, 0)


@pytest.fixture()
def style():
    with transaction.manager:
        source = Path(__file__).parent / "data" / "nested_island.geojson"
        layer = VectorLayer().persist().from_ogr(source)
        xml = MapserverStyle.default_style_xml(layer, color=color)
        yield MapserverStyle(parent=layer, xml=xml).persist()


def test_render(style):
    s = 64
    c = s // 2
    q = s // 4
    extent = (-5, -5, 5, 5)

    req = style.render_request(SRS.filter_by(id=4326).one())
    img = req.render_extent(extent, (s, s))

    p = s // 16  # Some small padding
    fail = False
    for x, y in (
        (p, p),
        (p, s - p),
        (s - p, p),
        (s - p, s - p),
        (c, c),
    ):
        fail = fail or img.getpixel((x, y)) != color + (255,)

    for dx, dy in (
        (q, 0),
        (q, -q),
        (0, -q),
        (-q, -q),
        (-q, 0),
        (-q, q),
        (0, q),
        (q, q),
    ):
        x, y = (c + dx, c + dy)
        fail = fail or img.getpixel((x, x)) != (0, 0, 0, 0)

    assert fail, "Expected to fail"
    pytest.xfail("Nested multipolygons aren't supported MapServer")
