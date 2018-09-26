import datetime
import os
import shutil

import pytest
from click.testing import CliRunner
from osgeo import gdal, osr, gdalnumeric

from scripts.modis.gdal_merge import process_folder
from snowrs import SourceFolder, TileMerger

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_TIFFS_DIR = os.path.join(TEST_ROOT, 'source_tiffs')
TEST_SOURCE_FOLDER = os.path.join(TEST_ROOT, 'source_folder')
RUN_YEAR = str(datetime.date.today().year)
DAY_OF_YEAR = '001'


class OutputFile:
    def __init__(self, source_folder, source_type):
        self.filename = self.get_file_name(source_type)
        file = gdal.Open(
            os.path.join(source_folder, self.filename)
        )

        self.bands = file.RasterCount
        _raster_band = file.GetRasterBand(1)
        self.band_type = _raster_band.DataType
        self.no_data_value = _raster_band.GetNoDataValue()
        self.band_values = gdalnumeric.BandReadAsArray(_raster_band)

        _projection = osr.SpatialReference(wkt=file.GetProjection())
        self.projection = _projection.GetAttrValue('geogcs')

        self.xsize = file.RasterXSize
        self.ysize = file.RasterYSize
        _geo_transform = file.GetGeoTransform()
        self.ulx = _geo_transform[0]
        self.uly = _geo_transform[3]
        self.pixel_width = _geo_transform[1]
        self.pixel_height = _geo_transform[5]

        del file

    @classmethod
    def get_file_name(cls, source_type):
        return RUN_YEAR + DAY_OF_YEAR + TileMerger.FILE_SUFFIX[source_type]


def get_source_folder(name):
    return os.path.join(
        TEST_SOURCE_FOLDER,
        RUN_YEAR,
        SourceFolder.FOLDER_TYPES[name],
        RUN_YEAR + DAY_OF_YEAR
    )


def create_source_folder(name):
    test_source_folder = get_source_folder(name)

    if os.path.exists(test_source_folder):
        shutil.rmtree(test_source_folder)

    shutil.copytree(TEST_TIFFS_DIR, test_source_folder)


def execute_runner(source_type):
    arguments = [
        '--source-folder', TEST_SOURCE_FOLDER,
        '--source-type', source_type
    ]

    cli_runner = CliRunner()
    return cli_runner.invoke(process_folder, arguments)


# Utility method to get a pytest marker from a test class
def get_cls_marker(cls, name):
    return next(
        (mark for mark in cls.pytestmark if mark.name == name)
    )


@pytest.fixture(scope='class', autouse=True)
def runner(request):
    mark = get_cls_marker(request.cls, 'runner_args')
    source_type = mark.kwargs['source_type']

    create_source_folder(source_type)

    request.cls.runner = execute_runner(source_type)
    request.cls.out_file = OutputFile(
        get_source_folder(source_type), source_type
    )
    request.cls.run_year = RUN_YEAR
    request.cls.day_of_year = DAY_OF_YEAR

    yield

    shutil.rmtree(TEST_SOURCE_FOLDER)
