from loguru import logger

from src.data.external.usgs_tesm.stages import download_tesm, load_tesm
from src.settings import Settings


@logger.catch
def process(settings: Settings, force: bool = False):
    logger.info("Starting Workunit Extent Spatial Metadata (WESM) pipeline")

    if not download_tesm.done(settings) or force:
        download_tesm.run(settings)
        force = True  # Run all following stages

    if not load_tesm.done(settings) or force:
        load_tesm.run(settings)


if __name__ == "__main__":
    settings = Settings()

    process(settings=settings)
