from pathlib import Path

from src.data.point_cloud.pipeline import select_tiles


def test_select_tiles():
    aoi_file = Path("data/raw/test_point.geojson").resolve()
    tile_index_file = Path("data/interim/tile_index.gpkg").resolve()

    result = select_tiles(aoi_file, tile_index_file)

    assert result.at[0, "tile_name"] == "15TXN689291"
    assert result.shape[0] == 1
    assert len(result.columns) == 3
