from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TileIndexSource:
    workunit: str
    zipped_shapefile: str
    tile_name_field: str
    ept_json_url: Optional[str] = None


@dataclass
class TileIndexPipelineConfig:
    tile_index_sources: list[TileIndexSource]

    @staticmethod
    def parse_toml(config_file: Path) -> TileIndexPipelineConfig:
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
        return TileIndexPipelineConfig(
            [TileIndexSource(**source) for source in config_data["tile_index_sources"]]
        )
