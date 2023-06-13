"""Module for loading raw data from external vector sources into and intermediate duckdb database."""
import os
from pathlib import Path

import duckdb
from loguru import logger

from src.settings import Settings, VectorSource


def load_layer(db: Path, from_gpkg: Path, layer: str, to_table: str) -> None:
    con = duckdb.connect(str(db))
    con.install_extension("spatial")
    con.load_extension("spatial")
    query = f"""
        CREATE TABLE {to_table} AS
        SELECT * FROM ST_Read('{from_gpkg}', sequential_layer_scan=TRUE, layer='{layer}');
    """
    con.execute(query).commit()


def load_vector_sources(settings: Settings) -> None:
    """Load vector sources into the duckdb database specified in settings.raw_data_pond.
    WARNING: Process is DESTRUCTIVE. The existing database will be fully deleted before loading vector data.
    """
    sources: list[VectorSource] = list(settings.vector_sources.values())
    db = settings.raw_data_pond

    # Always load into a fresh database
    if db.exists():
        os.remove(db)
    # Ensure parent directory exists
    db.parent.mkdir(parents=True, exist_ok=True)

    for src in sources:
        for lyr in src.load_layers:
            logger.info(
                f"LOAD: Loading {lyr.layer} from {src.filepath.name} into table {lyr.to_table}"
            )
            load_layer(
                db=db,
                from_gpkg=src.filepath,
                layer=lyr.layer,
                to_table=lyr.to_table,
            )


if __name__ == "__main__":
    settings = Settings()
    load_vector_sources(settings)
