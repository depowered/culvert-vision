from dataclasses import dataclass

import pytest
from pyproj import CRS
from shapely import Polygon

from src.data.point_cloud.point_source import vendor_classified_ground_points
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
        ept_filter_as_wkt=Polygon(
            ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0))
        ).wkt,
    )


@dataclass
class MochEPTData:
    ept_json_url: str = "https://fake.com/ept.json"


def test_vendor_classified_ground_points(tile_data: TileData):
    result = vendor_classified_ground_points(MochEPTData(), tile_data)

    expected = [
        {
            "tag": "raw_points",
            "type": "readers.ept",
            "filename": "https://fake.com/ept.json",
            "polygon": "POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))",
        },
        {
            "tag": "ground_only",
            "inputs": ["raw_points"],
            "type": "filters.range",
            "limits": "Classification[2:2]",
        },
        {
            "tag": "vendor_classified_ground_points",
            "inputs": ["ground_only"],
            "type": "filters.reprojection",
            "out_srs": "EPSG:6344",
        },
    ]

    assert result == expected
