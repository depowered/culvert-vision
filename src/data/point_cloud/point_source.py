from enum import StrEnum, auto
from functools import partial
from typing import Any, Callable

from geopandas import GeoDataFrame
from pandas import Series

StageDict = dict[str, str | int | float]


class PointSourceName(StrEnum):
    VENDOR_CLASSIFIED_GROUND_POINTS = auto()


def vendor_classified_ground_points(
    ept_json_url: str,
    ept_filter_as_wkt: str,
    to_epsg: int,
    tag: str = "vendor_classified_ground_points",
) -> list[StageDict]:
    return [
        {
            "tag": "raw_points",
            "type": "readers.ept",
            "filename": ept_json_url,
            "polygon": ept_filter_as_wkt,
        },
        {
            "tag": "ground_only",
            "inputs": ["raw_points"],
            "type": "filters.range",
            "limits": "Classification[2:2]",
        },
        {
            "tag": tag,
            "inputs": ["ground_only"],
            "type": "filters.reprojection",
            "out_srs": f"EPSG:{to_epsg}",
        },
    ]


def get_vendor_classified_ground_point_stages(enriched_tiles: GeoDataFrame) -> Series:
    return enriched_tiles.apply(
        lambda gdf: vendor_classified_ground_points(
            gdf.ept_json_url,
            gdf.ept_filter_as_wkt,
            gdf.to_epsg,
            gdf.point_source_tag,
        ),
        axis=1,
    )


PointSourceStagesFunc = Callable[[Any], Callable[[Any], list[StageDict]]]


def point_source_stages_func_factory(
    point_source_name: PointSourceName, **options
) -> PointSourceStagesFunc:
    if point_source_name == PointSourceName.VENDOR_CLASSIFIED_GROUND_POINTS:
        return partial(vendor_classified_ground_points, **options)
