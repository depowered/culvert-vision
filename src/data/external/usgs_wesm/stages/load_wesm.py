import subprocess

import psycopg
from loguru import logger
from psycopg import sql

from src.data.utils import pg_table_exists
from src.settings import Settings

_stage_name = "LOAD"


def run(settings: Settings):
    """Loads WESM data into PostGIS for workunits matching the ogr2ogr where filter
    specified in the settings."""
    wesm = settings.usgs_wesm
    logger.info(f"{_stage_name}: Creating and loading table {wesm.schemaname}.{wesm.tablename}")

    # Make sure the schema exists
    with psycopg.connect(settings.pg_dsn) as conn:
        query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {schemaname}").format(
            schemaname=sql.Identifier(wesm.schemaname)
        )
        conn.execute(query)
        conn.commit()

    # Remove the existing table before loading from source
    with psycopg.connect(settings.pg_dsn) as conn:
        query = sql.SQL("DROP TABLE IF EXISTS {schemaname}.{tablename};").format(
            schemaname=sql.Identifier(wesm.schemaname),
            tablename=sql.Identifier(wesm.tablename),
        )
        conn.execute(query)
        conn.commit()

    # Load data from sourcefile with ogr2ogr
    cmd = [
        "ogr2ogr",
        "-f",
        "PostgreSQL",
        f"{settings.pg_dsn}",
        "-nln",
        f"{wesm.schemaname}.{wesm.tablename}",
        "-where",
        f"{wesm.ogr2ogr_where}",
        f"{wesm.sourcefile}",
    ]
    subprocess.run(cmd)


def done(settings: Settings) -> bool:
    """Returns a bool indicating if the stage has been run."""
    # Check if the destination table exists
    exists = pg_table_exists(
        pg_dsn=settings.pg_dsn,
        schemaname=settings.usgs_wesm.schemaname,
        tablename=settings.usgs_wesm.tablename,
    )
    if exists:
        logger.info(f"{_stage_name}: Previous run satisfies stage")
    return exists
