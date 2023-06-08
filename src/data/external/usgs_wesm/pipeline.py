from loguru import logger

from src.data.external.usgs_wesm.stages import download_wesm, load_wesm
from src.settings import Settings


@logger.catch
def process(settings: Settings, force: bool = False):
    logger.info("Starting Workunit Extent Spatial Metadata (WESM) pipeline")

    if not download_wesm.done(settings) or force:
        download_wesm.run(settings)
        force = True # Run all following stages

    if not load_wesm.done(settings) or force:
        load_wesm.run(settings)


if __name__ == "__main__":
    settings = Settings()

    process(settings=settings)
