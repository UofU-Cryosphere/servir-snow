# Trimmed down version of gdal's distributed gdal_merge.py helper script

from osgeo import gdal, gdalnumeric

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
FILTER_TYPES = FILTER_TYPE_LIMITS.keys()
NO_DATA_VALUE = -999.0


class TileFile:
    """
    A class holding information for a tile file and method to copy band data
    into a target file.

    """

    def __init__(self, filename, source_type):
        """
        Initialize file_info from filename

        filename    -- Name of file to read.
        source_type -- Type of input file. This will determine the upper and
                       lower limit to filter band values.

        """
        tile_file = gdal.Open(filename)

        self.filename = filename
        self.bands = tile_file.RasterCount
        self.xsize = tile_file.RasterXSize
        self.ysize = tile_file.RasterYSize
        self.band_type = tile_file.GetRasterBand(1).DataType
        self.projection = tile_file.GetProjection()
        _geo_transform = tile_file.GetGeoTransform()
        self.ulx = _geo_transform[0]
        self.uly = _geo_transform[3]
        self.pixel_width = _geo_transform[1]
        self.pixel_height = _geo_transform[5]
        self.lrx = self.calculate_lr(self.ulx, self.pixel_width, self.xsize)
        self.lry = self.calculate_lr(self.uly, self.pixel_height, self.ysize)

        self.lower_limit = FILTER_TYPE_LIMITS[source_type]['lower']
        self.upper_limit = FILTER_TYPE_LIMITS[source_type]['upper']

        del tile_file

    def report(self):
        print('Filename: ' + self.filename)
        print('File Size: %dx%dx%d' % (self.xsize, self.ysize, self.bands))
        print('Pixel Size: %f x %f' % (self.pixel_width, self.pixel_height))
        print('UL:(%f,%f)   LR:(%f,%f)' %
              (self.ulx, self.uly, self.lrx, self.lry))

    @staticmethod
    def calculate_lr(ul, pixel_size, raster_size):
        return ul + pixel_size * raster_size

    def copy_into(self, output_file, source_band=1, target_band=1):
        """
        Copy data to target file and filter according to the type given in
        the initializer.

        output_file -- gdal.Dataset object for the file into which some or all
        of this file may be copied.
        """
        t_geotransform = output_file.GetGeoTransform()
        t_ulx = t_geotransform[0]
        t_uly = t_geotransform[3]
        t_pixel_width = t_geotransform[1]
        t_pixel_height = t_geotransform[5]

        # Intersection region
        tgw_ulx = max(t_ulx, self.ulx)
        if t_pixel_height < 0:
            tgw_uly = min(t_uly, self.uly)
        else:
            tgw_uly = max(t_uly, self.uly)

        # Target window in pixel coordinates.
        tw_xoff = int((tgw_ulx - t_ulx) / t_pixel_width + 0.1)
        tw_yoff = int((tgw_uly - t_uly) / t_pixel_height + 0.1)

        source_file = gdal.Open(self.filename, gdal.GA_ReadOnly)

        target_band = output_file.GetRasterBand(target_band)
        target_band.SetNoDataValue(NO_DATA_VALUE)

        source_values = gdalnumeric.BandReadAsArray(
            source_file.GetRasterBand(source_band),
            buf_type=gdal.GDT_Float32
        )

        # Filter by upper and lower band threshold values
        source_values[source_values < self.lower_limit] = NO_DATA_VALUE
        source_values[source_values > self.upper_limit] = NO_DATA_VALUE

        gdalnumeric.BandWriteArray(
            target_band, source_values, xoff=tw_xoff, yoff=tw_yoff
        )

        del source_values
        del source_file
