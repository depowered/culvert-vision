from shapely import Polygon

from src.data.point_cloud.point_source import (
    point_source_stages_func_factory,
    vendor_classified_ground_points,
)


def test_vendor_classified_ground_points():
    ept_json_url = "https://fake.com/ept.json"
    ept_filter_as_wkt = Polygon(
        ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0))
    ).wkt
    to_epsg = 6344

    result = vendor_classified_ground_points(ept_json_url, ept_filter_as_wkt, to_epsg)

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


def test_point_source_stages():
    point_source_name = "vendor_classified_ground_points"

    options = {
        "ept_json_url": "https://fake.com/ept.json",
        "tag": "test_tag",
    }
    tile_data = {
        "ept_filter_as_wkt": Polygon(
            ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0))
        ).wkt,
        "to_epsg": 6344,
    }

    func = point_source_stages_func_factory(point_source_name, **options)
    result = func(**tile_data)

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
            "tag": "test_tag",
            "inputs": ["ground_only"],
            "type": "filters.reprojection",
            "out_srs": "EPSG:6344",
        },
    ]

    assert result == expected
