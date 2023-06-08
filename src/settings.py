from datetime import date
from pathlib import Path

from pydantic import BaseModel, BaseSettings

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data/"
LOG_DIR = PROJECT_DIR / "logs/"


class WesmCsv(BaseModel):
    download_url = (
        "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/WESM.csv"
    )
    raw: Path = DATA_DIR / "external/usgs/WESM.csv"


class USGSWesm(BaseModel):
    download_url = (
        "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/WESM.gpkg"
    )
    sourcefile: Path = DATA_DIR / "external/usgs/WESM.gpkg"
    ogr2ogr_where: str = "workunit LIKE 'MN%' AND (ql = 'QL 0' OR ql = 'QL 1')"
    schemaname: str = "usgs"
    tablename: str = "wesm"


class Settings(BaseSettings):
    data_dir: Path = DATA_DIR
    log_file: Path = LOG_DIR / f"{date.today()}.log"

    # Database parameters
    postgres_db: str
    postgres_user: str
    postgres_pass: str
    postgres_published_port: int = 54320

    @property
    def pg_dsn(self) -> str:
        return "postgresql://{user}:{password}@localhost:{port}/{db_name}".format(
            user=self.postgres_user,
            password=self.postgres_pass,
            port=self.postgres_published_port,
            db_name=self.postgres_db,
        )

    wesm_csv: WesmCsv = WesmCsv()
    usgs_wesm: USGSWesm = USGSWesm()

    class Config:
        env_file = ".env"
