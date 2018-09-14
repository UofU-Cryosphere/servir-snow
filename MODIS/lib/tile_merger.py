import glob
import os

import gdalnumeric
import numpy
from osgeo import gdal, osr

from .tile_file import TileFile

NO_DATA_VALUE = -999.0

OUTPUT_PROJECTION = osr.SpatialReference()
OUTPUT_PROJECTION.ImportFromEPSG(4326)


class TileMerger:
    def __init__(self, source_folder, output_file_name, source_type):
        self.source_folder = source_folder
        self.output_file_name = output_file_name
        self.output_file = None
        self.source_type = source_type
        self.file_queue = []
        self.file_dimensions = {
            'ulx': [],
            'uly': [],
            'lrx': [],
            'lry': [],
        }

    @staticmethod
    def __calculate_pixel_size(right, left, width):
        return int((right - left) / width + 0.5)

    @staticmethod
    def __initialize_bands(output_file, bands_to_copy):
        na_values = numpy.full(
            (output_file.RasterYSize, output_file.RasterXSize),
            NO_DATA_VALUE
        )
        for band in bands_to_copy:
            target_band = output_file.GetRasterBand(band)
            target_band.SetNoDataValue(NO_DATA_VALUE)
            gdalnumeric.BandWriteArray(
                target_band, na_values
            )
        del na_values

    def __add_files_to_queue(self):
        for file in glob.glob(self.source_folder + TileFile.GLOB):
            file = TileFile(file, self.source_type)
            self.file_queue.append(file)

            # Remember dimensions for each file
            self.file_dimensions['ulx'].append(file.ulx)
            self.file_dimensions['uly'].append(file.uly)
            self.file_dimensions['lrx'].append(file.lrx)
            self.file_dimensions['lry'].append(file.lry)

    def __calculate_mosaic_dimension(self):
        self.file_dimensions['ulx'] = min(self.file_dimensions['ulx'])
        self.file_dimensions['uly'] = max(self.file_dimensions['uly'])
        self.file_dimensions['lrx'] = max(self.file_dimensions['lrx'])
        self.file_dimensions['lry'] = min(self.file_dimensions['lry'])

    def __cleanup_old_file(self):
        if os.path.isfile(self.output_file_name):
            os.remove(self.output_file_name)

    def __number_of_bands(self):
        return self.file_queue[0].bands

    def __pixel_height(self):
        return self.file_queue[0].pixel_height

    def __pixel_width(self):
        return self.file_queue[0].pixel_width

    def __init_output_file(self):
        x_size = self.__calculate_pixel_size(
            self.file_dimensions['lrx'],
            self.file_dimensions['ulx'],
            self.__pixel_width()
        )
        y_size = self.__calculate_pixel_size(
            self.file_dimensions['lry'],
            self.file_dimensions['uly'],
            self.__pixel_height()
        )

        gdal_driver = gdal.GetDriverByName('MEM')
        self.output_file = gdal_driver.Create(
            self.output_file_name,
            x_size,
            y_size,
            self.__number_of_bands(),
            gdal.GDT_Int16                # Int16 to enable NoData value of -999
        )

        self.output_file.SetGeoTransform(
            [self.file_dimensions['ulx'], self.__pixel_width(), 0,
             self.file_dimensions['uly'], 0, self.__pixel_height()]
        )
        self.output_file.SetProjection(self.file_queue[0].projection)

    def create_mosaic(self):
        self.__cleanup_old_file()

        self.__add_files_to_queue()

        if len(self.file_queue) == 0:
            # Indicate no source files to process
            return -1

        self.__calculate_mosaic_dimension()

        self.__init_output_file()

        files_processed = 0

        bands_to_copy = range(1, self.__number_of_bands() + 1)
        self.__initialize_bands(self.output_file, bands_to_copy)

        # Copy data from source files into output file.
        for file in self.file_queue:
            print("Processing file %4d of %4d, %6.3f%% completed"
                  % (files_processed + 1, len(self.file_queue),
                     files_processed * 100.0 / len(self.file_queue)))
            # file.report()

            [file.copy_into(self.output_file, band, band) for band in bands_to_copy]

            files_processed += 1

            del file

        # Indicate success
        return 1

    def project(self):
        print('Generating projected output file: ' + self.output_file_name)

        gdal.Warp(self.output_file_name, self.output_file, dstSRS='EPSG:4326')
