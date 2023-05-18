from __future__ import annotations

from typing import Protocol

import pdal

StageDict = dict[str, str | int | float]


class RasterBoundary(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def origin_x(self) -> float:
        ...

    @property
    def origin_y(self) -> float:
        ...

    def width(self, resolution: float) -> int:
        ...

    def height(self, resolution: float) -> int:
        ...

    def ept_filter_as_wkt(self, dist: float) -> str:
        ...


class PointSource(Protocol):
    @property
    def tag(self) -> str:
        ...

    def get_stages(self, raster_boundary: RasterBoundary) -> list[StageDict]:
        ...


class Product(Protocol):
    def get_stages(
        self, raster_boundary: RasterBoundary, point_source_tag: str
    ) -> list[StageDict]:
        ...


class PipelineFactory(Protocol):
    def get_stages(self, raster_boundary: RasterBoundary) -> pdal.Pipeline:
        ...
