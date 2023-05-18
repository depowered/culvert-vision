from dataclasses import dataclass

from shapely import Polygon


@dataclass
class Tile:
    name: str
    epsg_code: int
    ept_json_url: str
    geom: Polygon

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
