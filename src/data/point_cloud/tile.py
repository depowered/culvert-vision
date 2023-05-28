import math
from dataclasses import dataclass

from pyproj import CRS


@dataclass(slots=True)
class TileData:
    tile_name: str
    minx: float
    miny: float
    maxx: float
    maxy: float
    crs: CRS
    ept_filter_as_wkt: str

    @property
    def epsg(self) -> int:
        return self.crs.to_epsg()

    @property
    def origin_x(self) -> float:
        return self.minx

    @property
    def origin_y(self) -> float:
        return self.miny

    def width(self, resolution: float) -> int:
        return math.ceil((self.maxx - self.minx) / resolution)

    def height(self, resolution: float) -> int:
        return math.ceil((self.maxy - self.miny) / resolution)
