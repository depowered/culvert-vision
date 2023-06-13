from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings, HttpUrl, PostgresDsn

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data/"
LOG_DIR = PROJECT_DIR / "logs/"


class LoadLayer(BaseModel):
    layer: str
    to_table: str


class VectorSource(BaseModel):
    download_url: Optional[HttpUrl]
    filepath: Path
    schemaname: Optional[str]
    tablename: Optional[str]
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

    # Duckdb parameters
    raw_data_pond: Path = DATA_DIR / "interim/vector/raw_data_pond.duckdb"

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
            schemaname="raw",
            tablename="usgs_wesm",
            load_layers=[LoadLayer(layer="WESM", to_table="raw_usgs_wesm")],
        ),
        "usgs_opr_tesm": VectorSource(
            download_url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/FullExtentSpatialMetadata/OPR_TESM.gpkg",
            filepath=DATA_DIR / "external/usgs/OPR_TESM.gpkg",
            schemaname="raw",
            tablename="usgs_opr_tesm",
            load_layers=[LoadLayer(layer="OPR_TILE_SMD", to_table="raw_usgs_opr_tesm")],
        ),
        "mndnr_culvert_inventory": VectorSource(
            download_url="https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/struc_culvert_inventory_pub/gpkg_struc_culvert_inventory_pub.zip",
            filepath=DATA_DIR / "external/mndnr/struc_culvert_inventory_pub.gpkg",
            load_layers=[
                LoadLayer(layer="Bridge_Assessments", to_table="raw_mndnr_bridges"),
                LoadLayer(
                    layer="Stream_Crossing_Summary",
                    to_table="raw_mndnr_stream_crossings",
                ),
                LoadLayer(
                    layer="Culvert_Opening", to_table="raw_mndnr_culvert_openings"
                ),
            ],
        ),
        "mndnr_hydrography": VectorSource(
            download_url="https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/water_dnr_hydrography/gpkg_water_dnr_hydrography.zip",
            filepath=DATA_DIR / "external/mndnr/water_dnr_hydrography.gpkg",
            load_layers=[
                LoadLayer(layer="dnr_hydro_features_all", to_table="raw_mndnr_lakes"),
                LoadLayer(
                    layer="dnr_rivers_and_streams", to_table="raw_mndnr_watercourses"
                ),
            ],
        ),
        "mndnr_watershed_suite": VectorSource(
            download_url="https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/geos_dnr_watersheds/gpkg_geos_dnr_watersheds.zip",
            filepath=DATA_DIR / "external/mndnr/geos_dnr_watersheds.gpkg",
            load_layers=[
                LoadLayer(
                    layer="dnr_watersheds_dnr_level_08_all_catchments",
                    to_table="raw_mndnr_catchments_lvl08",
                ),
            ],
        ),
    }

    class Config:
        env_file = ".env"
