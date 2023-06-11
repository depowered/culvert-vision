import subprocess
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Protocol
from zipfile import ZIP_DEFLATED, ZipFile

import psycopg
import requests
from psycopg import sql
from psycopg.rows import namedtuple_row


def download_public_s3_asset(url: str, output_file: Path) -> Path:
    r = requests.get(url, stream=True)
    with open(output_file, "wb") as f:
        f.write(r.content)
    return output_file


def download_public_s3_asset_to_zip(
    url: str, output_dir: str, compression: int = ZIP_DEFLATED
) -> Path:
    filename = url.split("/")[-1]
    output_file = output_dir / f"{filename}.zip"
    r = requests.get(url, stream=True)
    with ZipFile(output_file, "w", compression=compression) as f:
        f.writestr(zinfo_or_arcname=filename, data=r.content)
    return output_file


def fetch_last_modified_datetime(url: str) -> datetime:
    r = requests.head(url)
    return parsedate_to_datetime(r.headers["Last-Modified"])


def make_parent_dirs_if_not_exist(file: Path) -> None:
    if not file.parent.exists():
        file.parent.mkdir(parents=True)


def pg_schema_exists(pg_dsn: str, schemaname: str) -> bool:
    """Returns a bool indiciating if the schema exists in the database."""
    with psycopg.connect(pg_dsn, row_factory=namedtuple_row) as conn:
        query = sql.SQL(
            """
            SELECT EXISTS(
                SELECT 1 FROM pg_catalog.pg_namespace
                WHERE nspname = {schemaname}
            )"""
        ).format(schemaname=sql.Literal(schemaname))
        record = conn.execute(query=query).fetchone()
        return record.exists


def pg_create_schema_if_not_exists(pg_dsn: str, schemaname) -> None:
    with psycopg.connect(pg_dsn) as conn:
        query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {schemaname}").format(
            schemaname=sql.Identifier(schemaname)
        )
        conn.execute(query)
        conn.commit()


def pg_table_exists(pg_dsn: str, schemaname: str, tablename: str) -> bool:
    """Returns a bool indiciating if the table exists in the database."""
    with psycopg.connect(pg_dsn, row_factory=namedtuple_row) as conn:
        query = sql.SQL(
            """
            SELECT EXISTS(
                SELECT 1 FROM pg_catalog.pg_tables
                WHERE
                    schemaname = {schemaname} AND
                    tablename = {tablename}
            )"""
        ).format(
            schemaname=sql.Literal(schemaname),
            tablename=sql.Literal(tablename),
        )
        record = conn.execute(query=query).fetchone()
        return record.exists


def pg_drop_table_if_exists(pg_dsn: str, schemaname: str, tablename: str) -> None:
    if not pg_schema_exists(pg_dsn=pg_dsn, schemaname=schemaname):
        # table can't exists if parent schema does not
        # The following query will raise an error if the schema doesn't exist
        return
    with psycopg.connect(pg_dsn) as conn:
        query = sql.SQL("DROP TABLE IF EXISTS {schemaname}.{tablename};").format(
            schemaname=sql.Identifier(schemaname),
            tablename=sql.Identifier(tablename),
        )
        conn.execute(query)
        conn.commit()


class VectorSource(Protocol):
    filepath: Path
    schemaname: str
    tablename: str


def pg_load_vector_source(pg_dsn: str, vector_src: VectorSource) -> None:
    nln = f"{vector_src.schemaname}.{vector_src.tablename}"
    input_file = f"{vector_src.filepath}"
    cmd = ["ogr2ogr", "-f", "PostgreSQL", "-progress", "-nln", nln, pg_dsn, input_file]
    subprocess.run(cmd)
