from pathlib import Path
from typing import Optional

import geopandas
import pandas as pd
from geopandas import GeoDataFrame

from .config import TileIndexConfig, TileIndexPipelineConfig


def _extract_tile_index(source: Path, tile_name_field: str) -> GeoDataFrame:
    return geopandas.read_file(filename=source, include_fields=[tile_name_field])


def _transform_tile_index(
    gdf: GeoDataFrame, tile_name_field: str, workunit: str, ept_json_url: Optional[str]
) -> GeoDataFrame:
    rename = {tile_name_field: "name"}
    assign = {"workunit": workunit, "ept_json_url": ept_json_url}
    astype = {"name": "string", "workunit": "string", "ept_json_url": "string"}
    return gdf.rename(columns=rename).assign(**assign).astype(astype)


def _extract_transform_tile_index(
    tile_index_source_dir: Path, config: TileIndexConfig
) -> GeoDataFrame:
    source = tile_index_source_dir / config.zipped_shapefile
    extracted = _extract_tile_index(source, config.tile_name_field)
    return _transform_tile_index(
        extracted, config.tile_name_field, config.workunit, config.ept_json_url
    )


def tile_index_pipeline(pipeline_config: TileIndexPipelineConfig) -> None:
    gdfs = (
        _extract_transform_tile_index(pipeline_config.tile_index_source_dir, config)
        for config in pipeline_config.tile_index_configs
    )
    contatinated: GeoDataFrame = pd.concat(gdfs)
    contatinated.to_parquet(pipeline_config.output_filepath)
