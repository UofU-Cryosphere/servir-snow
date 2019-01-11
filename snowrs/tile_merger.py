import glob
import os

from osgeo import gdal, gdalconst, gdalnumeric, osr


class TileMerger:
    BAND_DATA_TYPE = gdalconst.GDT_Int16  # Int16 to enable NoData value of -999
    BAND_NO_DATA_VALUE = -999.0
    BAND_NUMBER = 1
    BAND_METADATA = {
        'forcing': {
            'Description': 'Radiative forcing',
            'Unit': 'W/m^2',
        },
        'fraction': {
            'Description': 'Snow Cover',
            'Unit': '%',
        }
    }

    CREATE_OPTIONS = ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=IF_SAFER"]

    FILE_SUFFIX = {
        'forcing': '_rf.tif',
        'fraction': '_SCA.tif',
    }
    FILTER_TYPE_LIMITS = {
        'forcing': {
            'lower': 0.0,
            'upper': 400.0
        },
        'fraction': {
            'lower': 15.0,
            'upper': 100.0
        }
    }

    OUTPUT_FILE_DRIVER = gdal.GetDriverByName('MEM')
    OUTPUT_PROJECTION = osr.SpatialReference()
    OUTPUT_PROJECTION.ImportFromEPSG(4326)

    SOURCE_FILE_GLOB = '*[!_SCA,_rf].tif'
    SOURCE_FILE_PROJECTION = '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 ' \
                             '+a=6371007.181 +b=6371007.181 +units=m ' \
                             '+no_defs +nadgrids=@null +wktext'

    def __init__(self, source_folder, source_type):
        self.source_folder = source_folder
        self.output_file = None
        self.mosaic_vrt = None
        self.source_type = source_type
        self.file_queue = glob.glob(source_folder + self.SOURCE_FILE_GLOB)
        self.lower_limit = self.FILTER_TYPE_LIMITS[source_type]['lower']
        self.upper_limit = self.FILTER_TYPE_LIMITS[source_type]['upper']

    @property
    def output_file_name(self):
        return os.path.join(
            self.source_folder,
            os.path.basename(os.path.dirname(self.source_folder))
            + self.FILE_SUFFIX[self.source_type]
        )

    def __build_mosaic_vrt(self):
        file_name = os.path.join(self.source_folder, 'mosaic.vrt')
        vrt_options = gdal.BuildVRTOptions(
            outputSRS=self.SOURCE_FILE_PROJECTION,
        )
        self.mosaic_vrt = gdal.BuildVRT(
            file_name, self.file_queue, options=vrt_options
        )

    def __init_output_file(self):
        self.output_file = self.OUTPUT_FILE_DRIVER.Create(
            self.output_file_name,
            self.mosaic_vrt.RasterXSize, self.mosaic_vrt.RasterYSize,
            self.BAND_NUMBER, self.BAND_DATA_TYPE
        )

        self.output_file.SetGeoTransform(self.mosaic_vrt.GetGeoTransform())
        self.output_file.SetProjection(self.mosaic_vrt.GetProjection())

    def __copy_band_data(self):
        target_band = self.output_file.GetRasterBand(self.BAND_NUMBER)
        target_band.SetNoDataValue(self.BAND_NO_DATA_VALUE)

        source_values = gdalnumeric.BandReadAsArray(
            self.mosaic_vrt.GetRasterBand(self.BAND_NUMBER),
            buf_type=self.BAND_DATA_TYPE,
        )

        # Filter by upper and lower band threshold values
        source_values[
            (source_values < self.lower_limit) |
            (source_values > self.upper_limit)
            ] = self.BAND_NO_DATA_VALUE

        gdalnumeric.BandWriteArray(target_band, source_values)
        target_band.FlushCache()
        target_band.SetMetadata(self.BAND_METADATA[self.source_type])

        del target_band
        del source_values

    def create_mosaic(self):
        if len(self.file_queue) == 0:
            # Indicate no source files to process
            return -1

        self.__build_mosaic_vrt()
        self.__init_output_file()
        self.__copy_band_data()

        # Cleanup
        vrt_file_name = self.mosaic_vrt.GetDescription()
        del self.mosaic_vrt
        os.remove(vrt_file_name)

        # Indicate success
        return 1

    def project(self):
        print('Generating projected output file: ' + self.output_file_name)

        file = gdal.Warp(
            '', self.output_file, dstSRS=self.OUTPUT_PROJECTION, format='MEM'
        )
        gdal.Translate(
            self.output_file_name, file, creationOptions=self.CREATE_OPTIONS
        )
