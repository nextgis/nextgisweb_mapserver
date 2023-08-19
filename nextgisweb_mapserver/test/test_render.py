from pathlib import Path

import pytest
import transaction

from nextgisweb.env import DBSession

from nextgisweb.spatial_ref_sys import SRS
from nextgisweb.vector_layer import VectorLayer

from ..model import MapserverStyle

pytestmark = pytest.mark.usefixtures("ngw_resource_defaults")

data_path = Path(__file__).parent / "data"


@pytest.fixture()
def layer():
    with transaction.manager:
        source = data_path / "multipolygonz-duplicate.geojson"
        res = VectorLayer().persist().from_ogr(source)
        DBSession.flush()

    yield res


color = (200, 0, 0)


@pytest.fixture()
def style(layer):
    with transaction.manager:
        res = MapserverStyle(
            parent_id=layer.id,
            xml=MapserverStyle.default_style_xml(layer, color=color),
        ).persist()

        DBSession.flush()

        yield res


def test_render(style):
    srs = SRS.filter_by(id=4326).one()

    size = 64
    center = size // 2
    h = center // 2

    req = style.render_request(srs)
    extent = (-5, -5, 5, 5)
    img = req.render_extent(extent, (size, size))

    p = 5  # shade padding
    for x, y in (
        (p, p),
        (p, size - p),
        (size - p, p),
        (size - p, size - p),
        (center, center),
    ):
        assert img.getpixel((x, y)) == color + (255,)

    for dx, dy in (
        (h, 0),
        (h, -h),
        (0, -h),
        (-h, -h),
        (-h, 0),
        (-h, h),
        (0, h),
        (h, h),
    ):
        assert img.getpixel((center + dx, center + dy)) == (0, 0, 0, 0)
