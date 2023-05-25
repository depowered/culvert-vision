from pathlib import Path

from src.data.point_cloud.product import delauney_mesh_dem, product_stages_func_factory


def test_delauney_mesh_dem():
    result = delauney_mesh_dem(
        input_tag="vendor_classified_ground_points",
        resolution=0.5,
        width=2000,
        height=2000,
        origin_x=10.0,
        origin_y=10.0,
        output_dir=Path("/path/to/output"),
        name="tile_name",
    )

    expected = [
        {
            "tag": "delaunay_mesh",
            "inputs": ["vendor_classified_ground_points"],
            "type": "filters.delaunay",
        },
        {
            "tag": "faceraster",
            "type": "filters.faceraster",
            "inputs": ["delaunay_mesh"],
            "resolution": 0.5,
            "width": 2000,
            "height": 2000,
            "origin_x": 10.0,
            "origin_y": 10.0,
        },
        {
            "tag": "write_raster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": "/path/to/output/tile_name.tif",
            "gdaldriver": "GTiff",
            "gdalopts": "COMPRESS=DEFLATE",
            "data_type": "float32",
            "nodata": -999999,
        },
    ]

    assert result == expected


def test_stages_func_factory():
    product_name = "delauney_mesh_dem"
    options = {
        "input_tag": "vendor_classified_ground_points",
        "resolution": 0.5,
        "output_dir": Path("/path/to/output"),
    }
    tile_data = {
        "width": 2000,
        "height": 2000,
        "origin_x": 10.0,
        "origin_y": 10.0,
        "name": "tile_name",
    }

    func = product_stages_func_factory(product_name, **options)
    result = func(**tile_data)

    expected = [
        {
            "tag": "delaunay_mesh",
            "inputs": ["vendor_classified_ground_points"],
            "type": "filters.delaunay",
        },
        {
            "tag": "faceraster",
            "type": "filters.faceraster",
            "inputs": ["delaunay_mesh"],
            "resolution": 0.5,
            "width": 2000,
            "height": 2000,
            "origin_x": 10.0,
            "origin_y": 10.0,
        },
        {
            "tag": "write_raster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": "/path/to/output/tile_name.tif",
            "gdaldriver": "GTiff",
            "gdalopts": "COMPRESS=DEFLATE",
            "data_type": "float32",
            "nodata": -999999,
        },
    ]

    assert result == expected
