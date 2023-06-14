from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings, HttpUrl, PostgresDsn

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data/"
LOG_DIR = PROJECT_DIR / "logs/"
SQL_DUMP_DIR = DATA_DIR / "interim/vector/sql/"


class LoadLayer(BaseModel):
    layer: str
    to_table: str

    @property
    def sql_dump_file(self) -> Path:
        return SQL_DUMP_DIR / f"{self.to_table}_dump.sql"


class VectorSource(BaseModel):
    download_url: Optional[HttpUrl]
    filepath: Path
    load_layers: list[LoadLayer]


class Settings(BaseSettings):
    data_dir: Path = DATA_DIR
    log_file: Path = LOG_DIR / f"{date.today()}.log"

    # Postgres parameters
    postgres_db: str
    postgres_user: str
    postgres_pass: str
    postgres_host: str
    postgres_port: int

    @property
    def pg_dsn(self) -> PostgresDsn:
        return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(
            user=self.postgres_user,
            password=self.postgres_pass,
            host=self.postgres_host,
            port=self.postgres_port,
            db_name=self.postgres_db,
        )

    vector_sources: dict[str, VectorSource] = {
        "usgs_wesm": VectorSource(
            download_url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/WESM.gpkg",
            filepath=DATA_DIR / "external/usgs/WESM.gpkg",
            load_layers=[LoadLayer(layer="WESM", to_table="usgs_wesm")],
        ),
        "usgs_opr_tesm": VectorSource(
            download_url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/FullExtentSpatialMetadata/OPR_TESM.gpkg",
            filepath=DATA_DIR / "external/usgs/OPR_TESM.gpkg",
            load_layers=[LoadLayer(layer="OPR_TILE_SMD", to_table="usgs_opr_tesm")],
        ),
        "mndnr_culvert_inventory": VectorSource(
            download_url="https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/struc_culvert_inventory_pub/gpkg_struc_culvert_inventory_pub.zip",
            filepath=DATA_DIR / "external/mndnr/struc_culvert_inventory_pub.gpkg",
            load_layers=[
                LoadLayer(layer="Bridge_Assessments", to_table="mndnr_bridges"),
                LoadLayer(
                    layer="Stream_Crossing_Summary",
                    to_table="mndnr_stream_crossings",
                ),
                LoadLayer(layer="Culvert_Opening", to_table="mndnr_culvert_openings"),
            ],
        ),
        "mndnr_watershed_suite": VectorSource(
            download_url="https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/geos_dnr_watersheds/gpkg_geos_dnr_watersheds.zip",
            filepath=DATA_DIR / "external/mndnr/geos_dnr_watersheds.gpkg",
            load_layers=[
                LoadLayer(
                    layer="dnr_watersheds_dnr_level_08_all_catchments",
                    to_table="mndnr_catchments_lvl08",
                ),
            ],
        ),
    }

    class Config:
        env_file = ".env"
