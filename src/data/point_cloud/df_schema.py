import pandera
from pandera.typing.geopandas import GeoSeries
from pandera.typing.pandas import Series


class SelectedTilesSchema(pandera.DataFrameModel):
    tile_name: Series[str]
    workunit: Series[str]
    geometry: GeoSeries

    class Config:
        strict = "filter"


class TileDataSchema(pandera.DataFrameModel):
    tile_name: Series[str]
    minx: Series[float]
    miny: Series[float]
    maxx: Series[float]
    maxy: Series[float]
    crs: Series
    ept_filter_as_wkt: Series[str]

    class Config:
        strict = "filter"
