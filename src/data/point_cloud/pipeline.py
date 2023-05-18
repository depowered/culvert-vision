from dataclasses import dataclass

import pdal

from .interface import PointSource, Product, RasterBoundary


@dataclass
class PDALPipelineFactory:
    point_source: PointSource
    products: list[Product]

    def get_stages(self, raster_boundary: RasterBoundary) -> pdal.Pipeline:
        ...
