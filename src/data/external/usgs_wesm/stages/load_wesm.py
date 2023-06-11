from loguru import logger

from src.data.utils import (
    pg_create_schema_if_not_exists,
    pg_drop_table_if_exists,
    pg_load_vector_source,
    pg_table_exists,
)
from src.settings import Settings

_stage_name = "LOAD"


def run(settings: Settings):
    """Loads raw WESM data into PostGIS"""
    pg_dsn = settings.pg_dsn
    vector_src = settings.vector_sources["usgs_wesm"]
    logger.info(
        f"{_stage_name}: Loading table {vector_src.schemaname}.{vector_src.tablename}"
    )

    # Make sure the schema exists else load will fail
    pg_create_schema_if_not_exists(pg_dsn=pg_dsn, schemaname=vector_src.schemaname)

    # Remove the existing table before loading from source
    pg_drop_table_if_exists(
        pg_dsn=pg_dsn, schemaname=vector_src.schemaname, tablename=vector_src.tablename
    )

    # Load data from sourcefile with ogr2ogr
    pg_load_vector_source(pg_dsn=pg_dsn, vector_src=vector_src)


def done(settings: Settings) -> bool:
    """Returns a bool indicating if the stage has been run."""
    # Check if the destination table exists
    pg_dsn = settings.pg_dsn
    vector_src = settings.vector_sources["usgs_wesm"]
    exists = pg_table_exists(
        pg_dsn=pg_dsn,
        schemaname=vector_src.schemaname,
        tablename=vector_src.tablename,
    )
    if exists:
        logger.info(f"{_stage_name}: Previous run satisfies stage")
    return exists
