import json
import logging
from pathlib import Path

import geopandas
import numpy as np
import pdal
from geopandas import GeoDataFrame, GeoSeries
from pandas import Float32Dtype, Int64Dtype, Series
from pyproj import CRS

from src.data.point_cloud.ept import EPTData, fetch_ept_data
from src.data.point_cloud.point_source import get_vendor_classified_ground_point_stages
from src.data.point_cloud.product import get_delauney_mesh_dem_stages


def select_tiles(aoi_file: Path, tile_index_gpkg: Path) -> GeoDataFrame:
    aoi: GeoDataFrame = geopandas.read_file(aoi_file)
    return geopandas.read_file(tile_index_gpkg, mask=aoi.to_crs(6344))


def _calc_raster_width(gs: GeoSeries, resolution: float) -> Series:
    """Calculates the width of a raster in number of cells given a resolution.
    Always rounds up if the result of the resolution division is not a whole number."""
    return np.ceil(
        (gs.geometry.bounds["maxx"] - gs.geometry.bounds["minx"]) / resolution
    ).astype(Int64Dtype.type)


def _calc_raster_height(gs: GeoSeries, resolution: float) -> Series:
    """Calculates the height of a raster in number of cells given a resolution.
    Always rounds up if the result of the resolution division is not a whole number."""
    return np.ceil(
        (gs.geometry.bounds["maxy"] - gs.geometry.bounds["miny"]) / resolution
    ).astype(Int64Dtype.type)


def _calc_raster_origin_x(gs: GeoSeries) -> Series:
    """Returns the x value of the lower left boundary coordinate."""
    return gs.geometry.bounds["minx"].astype(Float32Dtype.type)


def _calc_raster_origin_y(gs: GeoSeries) -> Series:
    """Returns the y value of the lower left boundary coordinate."""
    return gs.geometry.bounds["miny"].astype(Float32Dtype.type)


def _calc_ept_filter_as_wkt(buffered_gs: GeoSeries, ept_crs: CRS) -> Series:
    return buffered_gs.to_crs(ept_crs).to_wkt().astype("string")


def enrich_tiles(
    selected_tiles: GeoDataFrame,
    ept_data: EPTData,
    point_source_tag: str,
    resolution: int,
    output_dir: Path,
) -> GeoDataFrame:
    assign = {
        "ept_json_url": ept_data.ept_json_url,
        "ept_filter_as_wkt": _calc_ept_filter_as_wkt(
            selected_tiles.buffer(10, join_style="mitre"), ept_data.crs
        ),
        "to_epsg": selected_tiles.crs.to_epsg(),
        "point_source_tag": point_source_tag,
        "resolution": resolution,
        "width": _calc_raster_width(selected_tiles.geometry, resolution),
        "height": _calc_raster_height(selected_tiles.geometry, resolution),
        "origin_x": _calc_raster_origin_x(selected_tiles.geometry),
        "origin_y": _calc_raster_origin_y(selected_tiles.geometry),
        "output_dir": output_dir,
    }
    return selected_tiles.assign(**assign)


def generate_pipeline_json(enriched_tiles: GeoDataFrame) -> GeoDataFrame:
    point_source_stages = get_vendor_classified_ground_point_stages(enriched_tiles)
    product_stages = get_delauney_mesh_dem_stages(enriched_tiles)
    assign = {"pipeline_json": (point_source_stages + product_stages).apply(json.dumps)}
    return enriched_tiles.filter(["name", "geometry"], axis="columns").assign(**assign)


def rasters_from_points_pipeline(
    aoi_file: Path, tile_index_file: Path, output_dir: Path
) -> None:
    """Runs a point cloud processing pipeline that produces raster products from
    hosted Entwire Point Tiles (ept).
    """
    logger = logging.getLogger(__name__)
    selected_tiles = select_tiles(aoi_file, tile_index_file)
    logger.info(
        "Intersection of AOI & tile index yielded %s tile(s)", selected_tiles.shape[0]
    )

    logger.info("Fetching Entwine Point Tile (EPT) data from AWS STAC Catalog")
    ept_data = fetch_ept_data(selected_tiles.at[0, "workunit"])

    enriched_tiles = enrich_tiles(
        selected_tiles=selected_tiles,
        ept_data=ept_data,
        point_source_tag="vendor_classified_ground_points",
        resolution=0.5,
        output_dir=output_dir,
    )

    stages = generate_pipeline_json(enriched_tiles)
    for tile in stages.to_dict("records"):
        logger.info("Running PDAL pipeline on tile %s", tile.get("name"))
        pipeline = pdal.Pipeline(tile.get("pipeline_stages"))
        pipeline.execute()
    logger.info("Complete")
