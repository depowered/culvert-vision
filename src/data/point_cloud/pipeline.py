import json
import logging
from pathlib import Path

import geopandas
import pdal
from geopandas import GeoDataFrame, GeoSeries
from pandas import DataFrame, Series
from pyproj import CRS

from src.data.point_cloud.df_schema import SelectedTilesSchema, TileDataSchema
from src.data.point_cloud.ept import EPTData, fetch_ept_data
from src.data.point_cloud.point_source import vendor_classified_ground_points
from src.data.point_cloud.product import delauney_mesh_dem
from src.data.point_cloud.tile import TileData


def select_tiles(aoi_file: Path, tile_index_gpkg: Path) -> GeoDataFrame:
    aoi: GeoDataFrame = geopandas.read_file(aoi_file)
    selected_tiles = geopandas.read_file(tile_index_gpkg, mask=aoi.to_crs(6344))
    validated: GeoDataFrame = SelectedTilesSchema.validate(selected_tiles)
    return validated


def select_tiles_by_location(
    aoi: GeoDataFrame, tile_index: GeoDataFrame
) -> GeoDataFrame:
    proj_aoi = aoi.to_crs(tile_index.crs)
    selected_tiles = geopandas.sjoin(
        left_df=tile_index, right_df=proj_aoi, how="inner", predicate="intersects"
    )
    validated: GeoDataFrame = SelectedTilesSchema.validate(selected_tiles)
    return validated


# TODO: Test
def _calc_ept_filter_as_wkt(geometry: GeoSeries, ept_crs: CRS) -> Series:
    return (
        geometry.buffer(10, join_style="mitre")
        .to_crs(ept_crs)
        .to_wkt()
        .astype("string")
    )


def generate_tile_data(
    selected_tiles: GeoDataFrame, ept_data: EPTData
) -> list[TileData]:
    tile_data_df = DataFrame(
        data={
            "tile_name": selected_tiles["tile_name"],
            "minx": selected_tiles.bounds["minx"],
            "miny": selected_tiles.bounds["miny"],
            "maxx": selected_tiles.bounds["maxx"],
            "maxy": selected_tiles.bounds["maxy"],
            "crs": selected_tiles.crs,
            "ept_filter_as_wkt": _calc_ept_filter_as_wkt(
                selected_tiles.geometry, ept_data.crs
            ),
        }
    )
    validated = TileDataSchema.validate(tile_data_df)
    tile_data = [TileData(**data) for data in validated.to_dict(orient="records")]
    return tile_data


# TODO: Test
def generate_pipelines(
    tile_data: list[TileData], ept_data: EPTData, resolution: float, output_dir: Path
) -> list[pdal.Pipeline]:
    pipelines = []
    for tile in tile_data:
        source_stages = vendor_classified_ground_points(ept_data, tile)
        product_stages = delauney_mesh_dem(tile, resolution, output_dir)
        pipeline_json = json.dumps(source_stages + product_stages)
        pipelines.append(pdal.Pipeline(pipeline_json))
    return pipelines


def rasters_from_points_pipeline(
    aoi: GeoDataFrame, tile_index: GeoDataFrame, output_dir: Path
) -> None:
    """Runs a point cloud processing pipeline that produces raster products from
    hosted Entwire Point Tiles (ept).
    """
    logger = logging.getLogger(__name__)
    selected_tiles = select_tiles_by_location(aoi, tile_index)
    logger.info(
        "Intersection of AOI & tile index yielded %s tile(s)", selected_tiles.shape[0]
    )

    logger.info("Fetching Entwine Point Tile (EPT) data from AWS STAC Catalog")
    ept_data = fetch_ept_data(selected_tiles["workunit"].iloc[0])

    tile_data = generate_tile_data(selected_tiles, ept_data)

    pipelines = generate_pipelines(
        tile_data=tile_data, ept_data=ept_data, resolution=0.5, output_dir=output_dir
    )

    for tile, pipeline in zip(tile_data, pipelines):
        logger.info("Executing pipeline for tile: %s", tile.tile_name)
        pipeline.execute()

    logger.info("Complete")


def _cli_create_point_cloud_products(
    aoi_file: Path, tile_index_file: Path, output_dir: Path
) -> None:
    def read_geo_file(f: Path) -> GeoDataFrame:
        return (
            geopandas.read_parquet(f)
            if f.suffix == ".parquet"
            else geopandas.read_file(f)
        )

    aoi = read_geo_file(aoi_file)
    tile_index = read_geo_file(tile_index_file)

    rasters_from_points_pipeline(aoi, tile_index, output_dir)
