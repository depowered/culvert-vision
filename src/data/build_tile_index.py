from pathlib import Path

import geopandas
import pandas as pd
from geopandas import GeoDataFrame
from pydantic import BaseModel, HttpUrl


class USGSWorkunitInfo(BaseModel):
    workunit: str
    workunit_id: int
    tile_index_zip: str
    tile_name_field: str
    ept_json_href: HttpUrl | None = None


def collect_workunit_info(workunit_info_dir: Path) -> list[USGSWorkunitInfo]:
    files = workunit_info_dir.glob("*.json")
    return [USGSWorkunitInfo.parse_file(file) for file in files]


def get_clean_tile_index_gdf(
    tile_index_dir: Path, source_info: USGSWorkunitInfo
) -> GeoDataFrame:
    source = tile_index_dir / source_info.tile_index_zip
    gdf: GeoDataFrame = geopandas.read_file(
        filename=source, include_fields=[source_info.tile_name_field]
    )
    return (
        gdf.rename(columns={source_info.tile_name_field: "name"})
        .assign(workunit_id=source_info.workunit_id, workunit=source_info.workunit)
        .astype({"name": "string", "workunit": "string"})
    )


def build_tile_index_gdf(tile_index_dir: Path, workunit_info_dir: Path) -> GeoDataFrame:
    wu_infos = collect_workunit_info(workunit_info_dir)
    gdfs = (
        get_clean_tile_index_gdf(tile_index_dir, source_info)
        for source_info in wu_infos
    )
    return pd.concat(gdfs)
