from dataclasses import dataclass

from .interface import RasterBoundary, StageDict


@dataclass
class PDALProduct:
    def get_stages(self, raster_boundary: RasterBoundary) -> list[StageDict]:
        ...
