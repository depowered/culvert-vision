from pathlib import Path

import pytest
from pyproj import CRS
from shapely import Polygon

from src.data.point_cloud.product import delauney_mesh_dem, product_stages_func_factory
from src.data.point_cloud.tile import TileData


@pytest.fixture()
def tile_data() -> TileData:
    return TileData(
        tile_name="15TXN689291",
        minx=10.0,
        miny=10.0,
        maxx=1010.0,
        maxy=1010.0,
        crs=CRS.from_epsg(6344),
        ept_filter_as_wkt=Polygon(
            ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0))
        ).wkt,
    )


def test_delauney_mesh_dem(tile_data: TileData):
    result = delauney_mesh_dem(
        input_tag="vendor_classified_ground_points",
        resolution=0.5,
        tile_data=tile_data,
        output_dir=Path("/path/to/output"),
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
            "tag": "write_faceraster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": "/path/to/output/dem_15TXN689291.tif",
            "gdaldriver": "GTiff",
            "gdalopts": "COMPRESS=DEFLATE",
            "data_type": "float32",
            "nodata": -999999,
        },
    ]

    assert result == expected


def test_intensity_raster(tile_data: TileData):
    product_name = "intensity_raster"
    options = {
        "input_tag": "vendor_classified_ground_points",
        "resolution": 0.5,
        "output_dir": Path("/path/to/output"),
    }

    func = product_stages_func_factory(product_name, **options)
    result = func(tile_data=tile_data)

    expected = [
        {
            "tag": "write_intensity_raster",
            "inputs": ["vendor_classified_ground_points"],
            "type": "writers.gdal",
            "dimension": "Intensity",
            "output_type": "all",
            "resolution": 0.5,
            "width": 2000,
            "height": 2000,
            "origin_x": 10.0,
            "origin_y": 10.0,
            "filename": "/path/to/output/intensity_15TXN689291.tif",
            "gdaldriver": "GTiff",
            "gdalopts": "COMPRESS=DEFLATE",
            "data_type": "uint16",
            "nodata": 65535,
        },
    ]

    assert result == expected


def test_stages_func_factory(tile_data: TileData):
    product_name = "delauney_mesh_dem"
    options = {
        "input_tag": "vendor_classified_ground_points",
        "resolution": 0.5,
        "output_dir": Path("/path/to/output"),
    }
    func = product_stages_func_factory(product_name, **options)
    result = func(tile_data=tile_data)

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
            "tag": "write_faceraster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": "/path/to/output/dem_15TXN689291.tif",
            "gdaldriver": "GTiff",
            "gdalopts": "COMPRESS=DEFLATE",
            "data_type": "float32",
            "nodata": -999999,
        },
    ]

    assert result == expected
