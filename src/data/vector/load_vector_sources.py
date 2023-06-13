from pathlib import Path

import duckdb
from loguru import logger

from src.settings import Settings, VectorSource


def load_layer(db: Path, from_gpkg: Path, layer: str, to_table: str) -> None:
    # Ensure db directory exists
    db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db))
    con.install_extension("spatial")
    con.load_extension("spatial")
    query = f"""
        CREATE OR REPLACE TABLE {to_table} AS
        SELECT * FROM ST_Read($gpkg, sequential_layer_scan=TRUE, layer=$layer)
    """
    params = {
        "gpkg": str(from_gpkg),
        "layer": layer,
    }
    con.execute(query=query, parameters=params).commit()


def load_vector_sources(settings: Settings) -> None:
    sources: list[VectorSource] = list(settings.vector_sources.values())

    for src in sources:
        for lyr in src.load_layers:
            logger.info(
                f"LOAD: Loading {lyr.layer} from {src.filepath.name} into table {lyr.to_table}"
            )
            load_layer(
                db=settings.raw_data_pond,
                from_gpkg=src.filepath,
                layer=lyr.layer,
                to_table=lyr.to_table,
            )


if __name__ == "__main__":
    settings = Settings()
    load_vector_sources(settings)
