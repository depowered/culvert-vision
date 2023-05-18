from __future__ import annotations

import logging
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv
from tile_index.config import TileIndexPipelineConfig
from tile_index.pipeline import tile_index_pipeline


@click.command()
@click.option(
    "-c",
    "--config-file",
    required=True,
    type=click.Path(exists=True),
    help="Tile index pipeline config definition as .toml",
)
def main(config_file: Path) -> None:
    """Runs a vector processing pipeline that cleans and merges USGS provided
    Tile Index shapefiles into a compressed geoparquet. Tiles are used to define
    the spatial extent of individual rasters generated from point cloud datasets.
    """
    logger = logging.getLogger(__name__)
    logger.info("Reading configuration settings from %s", config_file)
    config = TileIndexPipelineConfig.parse_toml(config_file)

    logger.info("Running pipeline on %s shapefiles", len(config.tile_index_configs))
    tile_index_pipeline(config)

    logger.info("Output tile index written to %s", config.output_filepath)


if __name__ == "__main__":
    # Load environment variables to reflect any changes to .env before continuing
    load_dotenv(find_dotenv())

    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
