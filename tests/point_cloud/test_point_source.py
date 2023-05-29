from src.data.point_cloud.point_source import vendor_classified_ground_points


class MochTileData:
    epsg: int = 6344
    ept_filter_as_wkt: str = "POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))"


class MochEPTData:
    ept_json_url: str = "https://fake.com/ept.json"


def test_vendor_classified_ground_points():
    result = vendor_classified_ground_points(MochEPTData(), MochTileData())

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
