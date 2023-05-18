from dataclasses import dataclass

from .tile_index.tile import Tile


@dataclass
class TileIndexPipelineConfig:
    ...


def main(cfg: TileIndexPipelineConfig) -> None:
    """Runs a vector processing pipeline that cleans and merges USGS provided
    Tile Index shapefiles into a compressed geoparquet. Tiles are used to define
    the spatial extent of individual rasters generated from point cloud datasets.
    """
    # Load tile index configuration parameters
    # Load and clean each shapefile
    # Concatinate all into a single GeoDataFrame
    # Write to the intirim data directory as a compressed geoparquet


if __name__ == "__main__":
    main()