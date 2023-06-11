from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings, HttpUrl, PostgresDsn

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data/"
LOG_DIR = PROJECT_DIR / "logs/"


class VectorSource(BaseModel):
    download_url: Optional[HttpUrl]
    filepath: Path
    schemaname: str
    tablename: str


class VectorSources(BaseModel):
    usgs_wesm: VectorSource = VectorSource(
        download_url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/WESM.gpkg",
        filepath=DATA_DIR / "external/usgs/WESM.gpkg",
        schemaname="raw",
        tablename="usgs_wesm",
    )
    usgs_opr_tesm: VectorSource = VectorSource(
        download_url="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/FullExtentSpatialMetadata/OPR_TESM.gpkg",
        filepath=DATA_DIR / "external/usgs/OPR_TESM.gpkg",
        schemaname="raw",
        tablename="usgs_opr_tesm",
    )


class Settings(BaseSettings):
    data_dir: Path = DATA_DIR
    log_file: Path = LOG_DIR / f"{date.today()}.log"

    # Database parameters
    postgres_db: str
    postgres_user: str
    postgres_pass: str
    postgres_published_port: int

    @property
    def pg_dsn(self) -> PostgresDsn:
        return "postgresql://{user}:{password}@localhost:{port}/{db_name}".format(
            user=self.postgres_user,
            password=self.postgres_pass,
            port=self.postgres_published_port,
            db_name=self.postgres_db,
        )

    vector_sources: VectorSources = VectorSources()

    class Config:
        env_file = ".env"
