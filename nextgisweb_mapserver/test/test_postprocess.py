from pathlib import Path

import pytest
import transaction

from nextgisweb.render import RenderPostprocess
from nextgisweb.spatial_ref_sys import SRS
from nextgisweb.vector_layer import VectorLayer

from ..model import MapserverStyle

pytestmark = pytest.mark.usefixtures("ngw_resource_defaults")


@pytest.fixture()
def style():
    with transaction.manager:
        source = Path(__file__).parent / "data" / "nested_island.geojson"
        layer = VectorLayer().persist().from_ogr(source)
        xml = MapserverStyle.default_style_xml(layer, color=(200, 0, 0))
        yield MapserverStyle(parent=layer, xml=xml).persist()


def test_mapserver_render_extent_applies_postprocess_on_padded_extent(style, monkeypatch):
    captured = {}

    def fake_apply_postprocess(img, postprocess, *, extent):
        captured["size"] = img.size
        captured["extent"] = extent
        captured["postprocess"] = postprocess
        return img

    monkeypatch.setattr("nextgisweb_mapserver.model.apply_postprocess", fake_apply_postprocess)

    req = style.render_request(
        SRS.filter_by(id=4326).one(), cond={"postprocess": RenderPostprocess(contrast=1.1)}
    )
    img = req.render_extent((-5.0, -5.0, 5.0, 5.0), (256, 256))

    assert img is not None
    assert img.size == (256, 256)
    assert captured["size"] == (384, 384)
    assert captured["extent"] == pytest.approx((-7.5, -7.5, 7.5, 7.5))
    assert captured["postprocess"].contrast == 1.1


def test_mapserver_render_tile_applies_postprocess_on_padded_extent(style, monkeypatch):
    captured = {}

    def fake_apply_postprocess(img, postprocess, *, extent):
        captured["size"] = img.size
        captured["extent"] = extent
        captured["postprocess"] = postprocess
        return img

    monkeypatch.setattr("nextgisweb_mapserver.model.apply_postprocess", fake_apply_postprocess)

    srs = SRS.filter_by(id=3857).one()
    tile = (0, 0, 0)
    req = style.render_request(srs, cond={"postprocess": RenderPostprocess(contrast=1.1)})
    img = req.render_tile(tile, 256)

    tile_extent = srs.tile_extent(tile)
    pad_x = (tile_extent[2] - tile_extent[0]) / 2
    pad_y = (tile_extent[3] - tile_extent[1]) / 2

    assert img is not None
    assert img.size == (256, 256)
    assert captured["size"] == (512, 512)
    assert captured["extent"] == pytest.approx(
        (
            tile_extent[0] - pad_x,
            tile_extent[1] - pad_y,
            tile_extent[2] + pad_x,
            tile_extent[3] + pad_y,
        )
    )
    assert captured["postprocess"].contrast == 1.1
