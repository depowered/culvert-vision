from loguru import logger

from src.data.utils import download_public_s3_asset, make_parent_dirs_if_not_exist
from src.settings import Settings

_stage_name = "DOWNLOAD"


def run(settings: Settings) -> None:
    """Downloads the Workunit Extent Spatial Metadata (WESM) asset from the USGS."""
    wesm = settings.usgs_wesm
    logger.info(
        f"{_stage_name}: Downloading {wesm.sourcefile.name} from {wesm.download_url}"
    )
    make_parent_dirs_if_not_exist(wesm.sourcefile)
    download_public_s3_asset(wesm.download_url, wesm.sourcefile)


def done(settings: Settings) -> bool:
    """Returns a bool indicating if the stage has been run."""
    exists = settings.usgs_wesm.sourcefile.exists()
    if exists:
        logger.info(f"{_stage_name}: Previous run satisfies stage")
    return exists
