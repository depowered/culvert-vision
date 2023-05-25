from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial
from pathlib import Path
from typing import Any, Callable

from geopandas import GeoDataFrame
from pandas import Series

StageDict = dict[str, str | int | float]


class ProductName(StrEnum):
    DELAUNEY_MESH_DEM = auto()


def delauney_mesh_dem(
    input_tag: str,
    resolution: float,
    width: int,
    height: int,
    origin_x: float,
    origin_y: float,
    output_dir: Path,
    name: str,
    prefix: str = "",
    postfix: str = "",
    extention: str = ".tif",
    gdaldriver: str = "GTiff",
    gdalopts: str = "COMPRESS=DEFLATE",
    data_type: str = "float32",
    nodata: float = -999999,
) -> list[StageDict]:
    file_path = output_dir / f"{prefix}{name}{postfix}{extention}"
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
            "width": width,
            "height": height,
            "origin_x": origin_x,
            "origin_y": origin_y,
        },
        {
            "tag": "write_raster",
            "inputs": ["faceraster"],
            "type": "writers.raster",
            "filename": str(file_path),
            "gdaldriver": gdaldriver,
            "gdalopts": gdalopts,
            "data_type": data_type,
            "nodata": nodata,
        },
    ]


def get_delauney_mesh_dem_stages(enriched_tiles: GeoDataFrame) -> Series:
    return enriched_tiles.apply(
        lambda gdf: delauney_mesh_dem(
            gdf.point_source_tag,
            gdf.resolution,
            gdf.width,
            gdf.height,
            gdf.origin_x,
            gdf.origin_y,
            gdf.output_dir,
            gdf["name"],
        ),
        axis=1,
    )


@dataclass
class PointDensityRaster:
    """A raster of the point count contained within each cell."""


@dataclass
class IntensityRaster:
    """A raster of point intensity values."""


ProductStagesFunc = Callable[[Any], Callable[[Any], list[StageDict]]]


def product_stages_func_factory(
    product_name: ProductName, **options
) -> ProductStagesFunc:
    if product_name == ProductName.DELAUNEY_MESH_DEM:
        return partial(delauney_mesh_dem, **options)
