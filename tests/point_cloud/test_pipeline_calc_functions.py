from geopandas import GeoSeries
from pandas import Float32Dtype, Int64Dtype, Series
from shapely import Polygon

from src.data.point_cloud.pipeline import (
    _calc_raster_height,
    _calc_raster_origin_x,
    _calc_raster_origin_y,
    _calc_raster_width,
)

# Test polygon with:
#   width = 10 @ resolution = 1
#   height = 20 @ resolution = 1
#   origin_x = 1.0
#   origin_y = 2.0
polygon = Polygon(((1.0, 2.0), (1.0, 22.0), (11.0, 22.0), (11.0, 2.0), (1.0, 2.0)))

single_gs = GeoSeries(data=[polygon])
multi_gs = GeoSeries(data=[polygon, polygon, polygon])


#####################################################################################
# _calc_raster_width tests
#####################################################################################


def test_calc_raster_width_single_gs():
    result = _calc_raster_width(single_gs, resolution=1)
    expected = Series(data=[10])

    assert result.shape == expected.shape
    assert result.iloc[0] == expected.iloc[0]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_width_multi_gs():
    result = _calc_raster_width(multi_gs, resolution=1)
    expected = Series(data=[10, 10, 10])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_width_half_resolution():
    result = _calc_raster_width(multi_gs, resolution=0.5)
    expected = Series(data=[20, 20, 20])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_width_one_third_resolution():
    result = _calc_raster_width(multi_gs, resolution=0.3)
    expected = Series(data=[34, 34, 34])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


#####################################################################################
# _calc_raster_height tests
#####################################################################################


def test_calc_raster_height_single_gs():
    result = _calc_raster_height(single_gs, resolution=1)
    expected = Series(data=[20])

    assert result.shape == expected.shape
    assert result.iloc[0] == expected.iloc[0]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_height_multi_gs():
    result = _calc_raster_height(multi_gs, resolution=1)
    expected = Series(data=[20, 20, 20])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_height_half_resolution():
    result = _calc_raster_height(multi_gs, resolution=0.5)
    expected = Series(data=[40, 40, 40])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


def test_calc_raster_height_one_third_resolution():
    result = _calc_raster_height(multi_gs, resolution=0.3)
    expected = Series(data=[67, 67, 67])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Int64Dtype.type


#####################################################################################
# _calc_raster_origin_x tests
#####################################################################################


def test_calc_raster_origin_x_single_gs():
    result = _calc_raster_origin_x(single_gs)
    expected = Series(data=[1.0])

    assert result.shape == expected.shape
    assert result.iloc[0] == expected.iloc[0]
    assert result.dtype == Float32Dtype.type


def test_calc_raster_origin_x_multi_gs():
    result = _calc_raster_origin_x(multi_gs)
    expected = Series(data=[1.0, 1.0, 1.0])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Float32Dtype.type


#####################################################################################
# _calc_raster_origin_y tests
#####################################################################################


def test_calc_raster_origin_y_single_gs():
    result = _calc_raster_origin_y(single_gs)
    expected = Series(data=[2.0])

    assert result.shape == expected.shape
    assert result.iloc[0] == expected.iloc[0]
    assert result.dtype == Float32Dtype.type


def test_calc_raster_origin_y_multi_gs():
    result = _calc_raster_origin_y(multi_gs)
    expected = Series(data=[2.0, 2.0, 2.0])

    assert result.shape == expected.shape
    assert result.iloc[2] == expected.iloc[2]
    assert result.dtype == Float32Dtype.type
