from enum import StrEnum, auto
from functools import partial
from pathlib import Path
from typing import Callable

from src.data.point_cloud.tile import TileData

PDALStage = dict


def _build_file_path_str(
    output_dir: Path, prefix: str, tile_name: str, postfix: str, extention: str
) -> str:
    return str(output_dir / f"{prefix}{tile_name}{postfix}{extention}")


def delauney_mesh_dem(
    tile_data: TileData,
    resolution: float,
    output_dir: Path,
    input_tag: str = "vendor_classified_ground_points",
    prefix: str = "dem_",
    postfix: str = "",
    extention: str = ".tif",
    gdaldriver: str = "GTiff",
    gdalopts: str = "COMPRESS=DEFLATE",
    data_type: str = "float32",
    nodata: float = -999999,
) -> list[PDALStage]:
    return [
        {
            "tag": "delaunay_mesh",
            "inputs": [input_tag],
            "type": "filters.delaunay",
        },
        {
            "tag": "faceraster",
            "inputs": ["delaunay_mesh"],
            "type": "filters.faceraster",
            "resolution": resolution,
            "width": tile_data.width(resolution),
            "height": tile_data.height(resolution),
            "origin_x": tile_data.origin_x,
            "origin_y": tile_data.origin_y,
        },
        {
            "tag": "write_faceraster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": _build_file_path_str(
                output_dir, prefix, tile_data.tile_name, postfix, extention
            ),
            "gdaldriver": gdaldriver,
            "gdalopts": gdalopts,
            "data_type": data_type,
            "nodata": nodata,
        },
    ]


def intensity_raster(
    tile_data: TileData,
    resolution: float,
    output_dir: Path,
    input_tag: str = "vendor_classified_ground_points",
    output_type: str = "all",
    prefix: str = "intensity_",
    postfix: str = "",
    extention: str = ".tif",
    gdaldriver: str = "GTiff",
    gdalopts: str = "COMPRESS=DEFLATE",
    data_type: str = "uint16",
    nodata: int = 65535,  # max of uint16
) -> list[PDALStage]:
    """A raster of point intensity values."""
    return [
        {
            "tag": "write_intensity_raster",
            "inputs": [input_tag],
            "type": "writers.gdal",
            "dimension": "Intensity",
            "output_type": output_type,
            "resolution": resolution,
            "width": tile_data.width(resolution),
            "height": tile_data.height(resolution),
            "origin_x": tile_data.origin_x,
            "origin_y": tile_data.origin_y,
            "filename": _build_file_path_str(
                output_dir, prefix, tile_data.tile_name, postfix, extention
            ),
            "gdaldriver": gdaldriver,
            "gdalopts": gdalopts,
            "data_type": data_type,
            "nodata": nodata,
        },
    ]


def point_density_raster() -> list[PDALStage]:
    """A raster of the point count contained within each cell."""
    raise NotImplementedError()


ProductStagesFunc = Callable[[TileData], list[PDALStage]]


class ProductName(StrEnum):
    DELAUNEY_MESH_DEM = auto()
    INTENSITY_RASTER = auto()
    POINT_DENSITY_RASTER = auto()


def product_stages_func_factory(
    product_name: ProductName, **options
) -> ProductStagesFunc:
    if product_name == ProductName.DELAUNEY_MESH_DEM:
        return partial(delauney_mesh_dem, **options)
    if product_name == ProductName.INTENSITY_RASTER:
        return partial(intensity_raster, **options)
    if product_name == ProductName.POINT_DENSITY_RASTER:
        return partial(point_density_raster, **options)


def generate_product_stages(
    tile_data: TileData, product_name: ProductName, product_options: dict
) -> list[PDALStage]:
    ...
