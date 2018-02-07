import numpy
import pytest

from .constants import RUN_YEAR, DAY_OF_YEAR
from .create_test_images import TILES, PROJECTION
from osgeo import gdal

NO_DATA_VALUE = -999.0


def tile_raster_band_values(upper, lower):
    values = numpy.array([*TILES.values()])
    values = values[values <= upper]
    values = values[values >= lower]

    return values


@pytest.mark.runner_args(source_type='forcing')
class TestForcing:
    def test_file_name(self):
        assert self.out_file.filename == RUN_YEAR + DAY_OF_YEAR + '_rf.tif'

    def test_raster_geo_transform(self):
        assert self.out_file.ulx == 0
        assert self.out_file.uly == 6
        assert self.out_file.pixel_width == 1
        assert self.out_file.pixel_height == -1

    def test_raster_size(self):
        assert self.out_file.xsize == 9
        assert self.out_file.ysize == 6

    def test_raster_projection(self):
        assert self.out_file.projection == PROJECTION.GetAttrValue('geogcs')

    def test_raster_band_properties(self):
        assert self.out_file.bands == 1
        assert self.out_file.band_type == gdal.GDT_Int16
        assert self.out_file.no_data_value == NO_DATA_VALUE

    def test_raster_band_filter_upper_limit(self):
        assert self.out_file.band_values.max() == 400

    def test_raster_band_filter_lower_limit(self):
        lower_limit = self.out_file.band_values[self.out_file.band_values < 0]
        lower_limit = lower_limit[lower_limit != NO_DATA_VALUE]
        assert len(lower_limit) == 0

    def test_raster_band_values(self):
        source_band_values = tile_raster_band_values(400, 0)
        mosaic_band_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert len(source_band_values) == len(mosaic_band_values)


@pytest.mark.runner_args(source_type='fraction')
class TestFraction:
    def test_file_name(self):
        assert self.out_file.filename == RUN_YEAR + DAY_OF_YEAR + '_SCA.tif'

    def test_raster_geo_transform(self):
        assert self.out_file.ulx == 0
        assert self.out_file.uly == 6
        assert self.out_file.pixel_width == 1
        assert self.out_file.pixel_height == -1

    def test_raster_size(self):
        assert self.out_file.xsize == 9
        assert self.out_file.ysize == 6

    def test_raster_projection(self):
        assert self.out_file.projection == PROJECTION.GetAttrValue('geogcs')

    def test_raster_band_properties(self):
        assert self.out_file.bands == 1
        assert self.out_file.band_type == gdal.GDT_Int16
        assert self.out_file.no_data_value == NO_DATA_VALUE

    def test_raster_band_filter_upper_limit(self):
        assert self.out_file.band_values.max() == 100

    def test_raster_band_filter_lower_limit(self):
        lower_limit = self.out_file.band_values[self.out_file.band_values < 0]
        lower_limit = lower_limit[lower_limit != NO_DATA_VALUE]
        assert len(lower_limit) == 0

    def test_raster_band_values(self):
        source_band_values = tile_raster_band_values(100, 15)
        mosaic_band_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert len(source_band_values) == len(mosaic_band_values)
