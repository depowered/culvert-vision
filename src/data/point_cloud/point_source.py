from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial
from typing import Any, Callable

from geopandas import GeoDataFrame
from pandas import Series
from pyproj import CRS
from pystac import Item
from pystac_client import Client

StageDict = dict[str, str | int | float]


@dataclass
class EPTData:
    workunit: str
    crs: CRS
    ept_json_url: str


def _get_first_matching_stac_item(stac_catalog_url: str, workunit: str) -> Item:
    client = Client.open(stac_catalog_url)
    item_links = [link for link in client.get_item_links() if workunit in link.href]
    return Item.from_file(item_links[0].href)


def fetch_ept_data(workunit: str) -> EPTData:
    stac_catalog_url = (
        "https://usgs-lidar-stac.s3-us-west-2.amazonaws.com/ept/catalog.json"
    )
    item = _get_first_matching_stac_item(stac_catalog_url, workunit)
    return EPTData(
        workunit=workunit,
        crs=CRS.from_epsg(item.properties["proj:epsg"]),
        ept_json_url=item.assets["ept.json"].href,
    )


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
