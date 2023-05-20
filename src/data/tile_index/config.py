from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests


@dataclass
class TileIndexSource:
    workunit: str
    zipped_shapefile: str
    tile_name_field: str
    ept_json_url: Optional[str] = None
    ept_epsg_code: Optional[str] = None

    def __post_init__(self) -> None:
        if self.ept_json_url is not None:
            try:
                r = requests.get(self.ept_json_url)
                r.raise_for_status()
            except requests.HTTPError:
                pass  # let self.ept_epsg_code stay as default
            data = r.json()
            self.ept_epsg_code = data.get("srs").get("horizontal")


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
