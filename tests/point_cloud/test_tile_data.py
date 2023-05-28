import pytest
from pyproj import CRS

from src.data.point_cloud.tile import TileData


@pytest.fixture()
def tile_data() -> TileData:
    return TileData(
        tile_name="15TXN689291",
        minx=1.0,
        miny=2.0,
        maxx=11.0,
        maxy=22.0,
        crs=CRS.from_epsg(6344),
        ept_filter_as_wkt="POLYGON (...)",
    )


def test_tile_data_epsg(tile_data: TileData):
    assert tile_data.epsg == 6344


def test_tile_data_origin_x(tile_data: TileData):
    assert tile_data.origin_x == 1.0


def test_tile_data_origin_y(tile_data: TileData):
    assert tile_data.origin_y == 2.0


def test_tile_data_height(tile_data: TileData):
    assert tile_data.height(1.0) == 20
    assert tile_data.height(0.5) == 40
    assert tile_data.height(0.3) == 67


def test_tile_data_width(tile_data: TileData):
    assert tile_data.width(1.0) == 10
    assert tile_data.width(0.5) == 20
    assert tile_data.width(0.3) == 34
