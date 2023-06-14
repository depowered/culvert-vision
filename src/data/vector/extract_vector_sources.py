"""Module for downloading external vector sources."""
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import requests
from loguru import logger
from pydantic import HttpUrl

from src.settings import Settings


def _get_last_modified_dt(filepath: Path) -> None:
    return datetime.fromtimestamp(filepath.lstat().st_mtime)


def _remote_is_newer(url: HttpUrl, source_file: Path) -> bool:
    """Uses If-Modified-Since request header to determine if the remote file is
    newer than the local copy.
    [MDN If-Modified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since)
    """
    last_modified = _get_last_modified_dt(filepath=source_file)
    headers = {"If-Modified-Since": format_datetime(dt=last_modified)}
    r = requests.head(url, headers=headers)
    return r.status_code == 200


def _download_gpkg(url: HttpUrl, source_file: Path) -> None:
    r = requests.get(url, stream=True)
    with open(source_file, "wb") as f:
        f.write(r.content)


def _download_and_unzip_gpkg(url: HttpUrl, source_file: Path) -> None:
    r = requests.get(url, stream=True)
    with NamedTemporaryFile("w+b") as tmp:
        tmp.write(r.content)
        with ZipFile(tmp, "r") as z:
            gpkg = [name for name in z.namelist() if ".gpkg" in name][0]
            z.extract(member=gpkg, path=source_file.parent)


def extract_vector_sources(settings: Settings) -> None:
    # Filter vector sources for those with a download_url
    vector_sources = [v for v in settings.vector_sources.values() if v.download_url]

    for src in vector_sources:
        source_file = src.filepath
        url = src.download_url

        if source_file.exists() and not _remote_is_newer(url, source_file):
            logger.info(f"EXTRACT: Local {source_file.name} is up-to-date")
            continue

        logger.info(f"EXTRACT: Downloading {source_file.name}")
        # Ensure file directory exists
        source_file.parent.mkdir(parents=True, exist_ok=True)
        if url.endswith(".zip"):
            _download_and_unzip_gpkg(url, source_file)
        else:
            _download_gpkg(url, source_file)


if __name__ == "__main__":
    settings = Settings()
    extract_vector_sources(settings)
