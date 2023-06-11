from loguru import logger

from src.data.utils import download_public_s3_asset, make_parent_dirs_if_not_exist
from src.settings import Settings

_stage_name = "DOWNLOAD"


def run(settings: Settings) -> None:
    """Downloads the Workunit Extent Spatial Metadata (WESM) asset from the USGS."""
    vector_src = settings.vector_sources.usgs_opr_tesm
    logger.info(
        f"{_stage_name}: Downloading {vector_src.filepath.name} from {vector_src.download_url}"
    )
    make_parent_dirs_if_not_exist(vector_src.filepath)
    download_public_s3_asset(vector_src.download_url, vector_src.filepath)


def done(settings: Settings) -> bool:
    """Returns a bool indicating if the stage has been run."""
    vector_src = settings.vector_sources.usgs_opr_tesm
    exists = vector_src.filepath.exists()
    if exists:
        logger.info(f"{_stage_name}: Previous run satisfies stage")
    return exists
