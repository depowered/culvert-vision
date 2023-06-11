from pathlib import Path

import geopandas

from src.data.point_cloud.pipeline import select_tiles, select_tiles_by_location


def test_select_tiles():
    aoi_file = Path("data/raw/test_point.geojson").resolve()
    tile_index_file = Path("data/interim/tile_index.gpkg").resolve()

    result = select_tiles(aoi_file, tile_index_file)

    assert result.at[0, "tile_name"] == "15TXN689290"
    assert result.shape[0] == 1
    assert len(result.columns) == 3


def test_select_tiles_by_location():
    aoi_file = Path("data/raw/test_point.geojson").resolve()
    aoi = geopandas.read_file(aoi_file)

    tile_index_file = Path("data/interim/tile_index.parquet").resolve()
    tile_index = geopandas.read_parquet(tile_index_file)

    result = select_tiles_by_location(tile_index, aoi)

    assert result.shape[0] == 1
    assert result["tile_name"].iloc[0] == "15TXN689290"
    assert len(result.columns) == 3
