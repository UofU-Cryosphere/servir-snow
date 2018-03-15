import gdal_merge
import shutil

from .constants import *
from click.testing import CliRunner
from gdal_merge import FILTER_TYPES
from osgeo import gdal, gdalnumeric, osr


def get_source_folder(name):
    return os.path.join(
        TEST_SOURCE_FOLDER,
        RUN_YEAR,
        FILTER_TYPES[name]['source_folder'],
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
    return cli_runner.invoke(gdal_merge.process_folder, arguments)


class OutputFile:
    def __init__(self, source_type):
        self.filename = self.get_file_name(source_type)
        file = gdal.Open(
            os.path.join(get_source_folder(source_type), self.filename)
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
        return RUN_YEAR + DAY_OF_YEAR + FILTER_TYPES[source_type]['file_suffix']
