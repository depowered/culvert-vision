from dataclasses import dataclass

from .interface import RasterBoundary, StageDict


@dataclass
class EPTPointSource:
    def get_stages(self, raster_boundary: RasterBoundary) -> list[StageDict]:
        ...
