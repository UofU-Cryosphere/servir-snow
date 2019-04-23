import pytest
from numpy.testing import assert_equal
from osgeo import gdal

from tests.setup_scripts.create_test_images import TILE_VALUES, PROJECTION

NO_DATA_VALUE = -999.0


def tile_raster_band_values(upper, lower):
    return TILE_VALUES[(TILE_VALUES >= lower) & (TILE_VALUES <= upper)]


@pytest.mark.runner_args(source_type='forcing')
class TestForcing:
    def test_file_name(self):
        filename = self.run_year + self.day_of_year + '_rf.tif'
        assert self.out_file.filename == filename

    @pytest.mark.skip(reason="TODO - Create test files with MODIS projection")
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
        data_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert data_values.min() == 0

    def test_raster_band_no_data_value(self):
        no_data = self.out_file.band_values[
            self.out_file.band_values == NO_DATA_VALUE
        ]
        assert len(no_data) > 0

    @pytest.mark.skip(reason="TODO - Create test files with MODIS projection")
    def test_raster_band_values(self):
        source_band_values = tile_raster_band_values(400, 0)
        mosaic_band_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert_equal(source_band_values, mosaic_band_values)


@pytest.mark.runner_args(source_type='fraction')
class TestFraction:
    def test_file_name(self):
        filename = self.run_year + self.day_of_year + '_SCA.tif'
        assert self.out_file.filename == filename

    @pytest.mark.skip(reason="TODO - Create test files with MODIS projection")
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
        data_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert data_values.min() == 15

    def test_raster_band_no_data_value(self):
        no_data = self.out_file.band_values[
            self.out_file.band_values == NO_DATA_VALUE
        ]
        assert len(no_data) > 0

    @pytest.mark.skip(reason="TODO - Create test files with MODIS projection")
    def test_raster_band_values(self):
        source_band_values = tile_raster_band_values(100, 15)
        mosaic_band_values = self.out_file.band_values[
            self.out_file.band_values != NO_DATA_VALUE
        ]
        assert_equal(source_band_values, mosaic_band_values)
