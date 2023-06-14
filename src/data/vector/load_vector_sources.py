"""Load PostGIS database from dumped COPY statements."""
import subprocess
from pathlib import Path

from loguru import logger

from src.settings import Settings, VectorSource


def _load_from_pgsql(dump_file: Path) -> None:
    script = Path(__file__).resolve().parent / "scripts/load_from_pgsql.sh"
    subprocess.run(["sh", script, str(dump_file)])


def load_vector_sources(settings: Settings) -> None:
    vector_sources: list[VectorSource] = list(settings.vector_sources.values())

    for src in vector_sources:
        for lyr in src.load_layers:
            dump_file = lyr.sql_dump_file
            logger.info(f"LOAD: Creating raw.{lyr.to_table} from {dump_file.name}")
            _load_from_pgsql(dump_file)


if __name__ == "__main__":
    settings = Settings()
    load_vector_sources(settings)
