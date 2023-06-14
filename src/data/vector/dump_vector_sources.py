"""Dump vector sources to COPY statements for importing to PostGIS."""
import subprocess
from pathlib import Path

from loguru import logger

from src.settings import Settings, VectorSource


def _source_in_newer(source_file: Path, dump_file: Path) -> bool:
    return source_file.stat().st_mtime > dump_file.stat().st_mtime


def _dump_to_pgsql(
    dump_file: Path, source_file: Path, layer: str, to_table: str
) -> None:
    script = Path(__file__).resolve().parent / "scripts/dump_to_pgsql.sh"
    subprocess.run(["sh", script, str(dump_file), str(source_file), layer, to_table])


def dump_vector_sources(settings: Settings) -> None:
    vector_sources: list[VectorSource] = list(settings.vector_sources.values())

    for src in vector_sources:
        source_file = src.filepath
        for lyr in src.load_layers:
            dump_file = lyr.sql_dump_file
            layer = lyr.layer
            to_table = lyr.to_table

            if dump_file.exists() and not _source_in_newer(source_file, dump_file):
                logger.info(f"DUMP: {dump_file.name} is up-to-date")
                continue

            logger.info(f"DUMP: Dumping {source_file.name}:{layer} to {dump_file.name}")
            # Ensure sql dump directory exists
            dump_file.parent.mkdir(parents=True, exist_ok=True)
            _dump_to_pgsql(dump_file, source_file, layer, to_table)


if __name__ == "__main__":
    settings = Settings()
    dump_vector_sources(settings)
