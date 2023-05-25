import logging
from pathlib import Path

import click

from src.data.tile_index.config import TileIndexPipelineConfig
from src.data.tile_index.pipeline import tile_index_pipeline


@click.command()
@click.option(
    "-c",
    "--config-file",
    required=True,
    type=click.Path(
        exists=True, resolve_path=True, dir_okay=False, file_okay=True, path_type=Path
    ),
    help="Tile index pipeline config definition as .toml",
)
@click.option(
    "-i",
    "--input-dir",
    required=True,
    type=click.Path(
        exists=True, resolve_path=True, dir_okay=True, file_okay=False, path_type=Path
    ),
    help="Directory containing the zipped shapefiles to process",
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    type=click.Path(resolve_path=True, dir_okay=False, file_okay=True, path_type=Path),
    help="Output file. Must end with .parquet",
)
def main(config_file: Path, input_dir: Path, output_file: Path) -> None:
    """Runs a vector processing pipeline that cleans and merges USGS provided
    Tile Index shapefiles into a compressed geoparquet. Tiles are used to define
    the spatial extent of individual rasters generated from point cloud datasets.
    """
    logger = logging.getLogger(__name__)
    logger.info("Reading configuration settings from %s", config_file)
    config = TileIndexPipelineConfig.parse_toml(config_file)

    logger.info("Running pipeline on %s shapefiles", len(config.tile_index_sources))
    tile_index_pipeline(config, input_dir, output_file)

    logger.info("Output tile index written to %s", output_file)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
