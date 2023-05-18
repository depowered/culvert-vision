from dataclasses import dataclass

from .point_cloud.interface import PipelineFactory, PointSource, Product, RasterBoundary


@dataclass
class PointCloudPipelineConfig:
    ...


def main(cfg: PointCloudPipelineConfig) -> None:
    """Runs a point cloud processing pipeline that produces raster products from
    hosted Entwire Point Tiles (ept).
    """
    # Read Area of Interest (AOI) geometry into a GeoDataFrame
    # Select tiles by intersecting the AOI with the Tile Index
    # Extract selected tiles into Tile objects for processing
    # Initialize the Point Source object
    # Initialize the Product object(s)
    # Create a PDAL Pipeline Factory object
    # Iterate over the Tiles, executing a PDAL pipeline for each


if __name__ == "__main__":
    main()