from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TileIndexConfig:
    workunit: str
    zipped_shapefile: str
    tile_name_field: str
    ept_json_url: Optional[str] = None


@dataclass
class TileIndexPipelineConfig:
    tile_index_source_dir: Path
    output_filepath: Path
    tile_index_configs: list[TileIndexConfig]

    @staticmethod
    def parse_toml(config_file: Path) -> TileIndexPipelineConfig:
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
        # Load data directory from the environment to prepend to tile_index_source_dir
        data_dir = Path(os.getenv("CULVERT_VISION_DATA_DIR")).resolve()
        tile_index_source_dir = data_dir / config_data["tile_index_source_dir"]
        output_filepath = data_dir / config_data["output_filepath"]
        tile_index_configs = [
            TileIndexConfig(**config) for config in config_data["tile_index_configs"]
        ]
        return TileIndexPipelineConfig(
            tile_index_source_dir, output_filepath, tile_index_configs
        )
