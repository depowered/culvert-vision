import logging
from pathlib import Path

import click

from src.data.point_cloud.pipeline import _cli_create_point_cloud_products


@click.command()
@click.option(
    "--aoi-file",
    required=True,
    type=click.Path(resolve_path=True, dir_okay=False, file_okay=True, path_type=Path),
    help="Area of Interest (aoi) geometry used to select tiles",
)
@click.option(
    "--tile-index-file",
    required=True,
    type=click.Path(resolve_path=True, dir_okay=False, file_okay=True, path_type=Path),
    help="Tile index geopackage",
)
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(resolve_path=True, dir_okay=True, file_okay=False, path_type=Path),
    help="Output directory to write products",
)
def main(aoi_file: Path, tile_index_file: Path, output_dir: Path) -> None:
    """Runs a point cloud processing pipeline that produces raster products from
    hosted Entwire Point Tiles (ept).
    """
    _cli_create_point_cloud_products(aoi_file, tile_index_file, output_dir)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
