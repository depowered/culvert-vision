from pathlib import Path

from pyproj import CRS

from src.data.point_cloud.ept import EPTData
from src.data.point_cloud.pipeline import generate_tile_data, select_tiles
from src.data.point_cloud.tile import TileData


def test_generate_tile_data():
    aoi_file = Path("data/raw/test_point.geojson").resolve()
    tile_index_file = Path("data/interim/tile_index.gpkg").resolve()
    selected_tiles = select_tiles(aoi_file, tile_index_file)
    ept_data = EPTData(
        workunit="MN_RainyLake_1_2020",
        crs=CRS.from_epsg(6344),
        ept_json_url="https://s3-us-west-2.amazonaws.com/usgs-lidar-public/MN_RainyLake_1_2020/ept.json",
    )

    result = generate_tile_data(selected_tiles, ept_data)

    assert len(result) == 1
    assert isinstance(result[0], TileData)
    assert result[0].tile_name == "15TXN689290"
