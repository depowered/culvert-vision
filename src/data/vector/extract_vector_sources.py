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


def get_last_modified_dt(filepath: Path) -> None:
    return datetime.fromtimestamp(filepath.lstat().st_mtime)


def remote_is_newer(url: HttpUrl, filepath: Path) -> bool:
    """Uses If-Modified-Since request header to determine if the remote file is
    newer than the local copy.
    [MDN If-Modified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since)
    """
    last_modified = get_last_modified_dt(filepath=filepath)
    headers = {"If-Modified-Since": format_datetime(dt=last_modified)}
    r = requests.head(url, headers=headers)
    return r.status_code == 200


def download_gpkg(url: HttpUrl, filepath: Path) -> None:
    r = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        f.write(r.content)


def download_and_unzip_gpkg(url: HttpUrl, filepath: Path) -> None:
    r = requests.get(url, stream=True)
    with NamedTemporaryFile("w+b") as tmp:
        tmp.write(r.content)
        with ZipFile(tmp, "r") as z:
            gpkg = [name for name in z.namelist() if ".gpkg" in name][0]
            z.extract(member=gpkg, path=filepath.parent)


def extract_vector_sources(settings: Settings) -> None:
    # Filter vector sources for those with a download_url
    vector_sources = [v for _, v in settings.vector_sources.items() if v.download_url]

    for vector_src in vector_sources:
        filepath = vector_src.filepath
        url = vector_src.download_url
        if filepath.exists() and not remote_is_newer(url, filepath):
            logger.info(f"EXTRACT: Local {filepath.name} is up-to-date")
            continue
        logger.info(f"EXTRACT: Downloading {filepath.name}")
        # Ensure file directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if url.endswith(".zip"):
            download_and_unzip_gpkg(url, filepath)
        else:
            download_gpkg(url, filepath)


if __name__ == "__main__":
    settings = Settings()
    extract_vector_sources(settings)
