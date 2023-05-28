from pathlib import Path
from typing import Optional

import geopandas
import pandas as pd
from geopandas import GeoDataFrame

from src.data.tile_index.config import TileIndexPipelineConfig, TileIndexSource


def _extract_tile_index(zipped_shapefile: Path, tile_name_field: str) -> GeoDataFrame:
    return geopandas.read_file(
        filename=zipped_shapefile, include_fields=[tile_name_field]
    )


def _transform_tile_index(
    gdf: GeoDataFrame,
    tile_name_field: str,
    workunit: str,
    ept_json_url: Optional[str],
    ept_epsg_code: Optional[str],
) -> GeoDataFrame:
    rename = {tile_name_field: "tile_name"}
    assign = {
        "workunit": workunit,
        "ept_json_url": ept_json_url,
        "ept_epsg_code": ept_epsg_code,
    }
    astype = {
        "tile_name": "string",
        "workunit": "string",
        "ept_json_url": "string",
        "ept_epsg_code": "string",
    }
    return gdf.rename(columns=rename).assign(**assign).astype(astype)


def _extract_transform_tile_index(
    source: TileIndexSource, input_dir: Path
) -> GeoDataFrame:
    zipped_shapefile = input_dir / source.zipped_shapefile
    extracted = _extract_tile_index(zipped_shapefile, source.tile_name_field)
    return _transform_tile_index(
        extracted,
        source.tile_name_field,
        source.workunit,
        source.ept_json_url,
        source.ept_epsg_code,
    )


def tile_index_pipeline(
    config: TileIndexPipelineConfig, input_dir: Path, output_file: Path
) -> None:
    gdfs = (
        _extract_transform_tile_index(source, input_dir)
        for source in config.tile_index_sources
    )
    contatinated: GeoDataFrame = pd.concat(gdfs)
    if output_file.suffix == ".parquet":
        contatinated.to_parquet(output_file)
    else:
        contatinated.to_file(output_file)
