# Trimmed down version of gdal's distributed gdal_merge.py helper script

from osgeo import gdal


class TileFile:
    """A class holding information about a GDAL file."""

    def __init__(self, filename):
        """
        Initialize file_info from filename

        filename -- Name of file to read.

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
        Copy this files image into target file.

        This method will compute the overlap area of the file_info objects
        file, and the target gdal.Dataset object, and copy the image data
        for the common window area.  It is assumed that the files are in
        a compatible projection ... no checking or warping is done.  However,
        if the destination file is a different resolution, or different
        image pixel type, the appropriate resampling and conversions will
        be done (using normal GDAL promotion/demotion rules).

        output_file -- gdal.Dataset object for the file into which some or all
        of this file may be copied.

        Returns 1 on success (or if nothing needs to be copied), and zero one
        failure.
        """
        t_geotransform = output_file.GetGeoTransform()
        t_ulx = t_geotransform[0]
        t_uly = t_geotransform[3]
        t_pixel_width = t_geotransform[1]
        t_pixel_height = t_geotransform[5]
        t_lrx = self.calculate_lr(t_ulx, t_pixel_width, output_file.RasterXSize)
        t_lry = self.calculate_lr(
            t_uly, t_pixel_height, output_file.RasterYSize
        )

        # figure out intersection region
        tgw_ulx = max(t_ulx, self.ulx)
        tgw_lrx = min(t_lrx, self.lrx)
        if t_pixel_height < 0:
            tgw_uly = min(t_uly, self.uly)
            tgw_lry = max(t_lry, self.lry)
        else:
            tgw_uly = max(t_uly, self.uly)
            tgw_lry = min(t_lry, self.lry)

        # compute target window in pixel coordinates.
        tw_xoff = int((tgw_ulx - t_ulx) / t_pixel_width + 0.1)
        tw_yoff = int((tgw_uly - t_uly) / t_pixel_height + 0.1)
        tw_xsize = int((tgw_lrx - t_ulx) / t_pixel_width + 0.5) - tw_xoff
        tw_ysize = int((tgw_lry - t_uly) / t_pixel_height + 0.5) - tw_yoff

        if tw_xsize < 1 or tw_ysize < 1:
            return 1

        # Compute source window in pixel coordinates.
        sw_xoff = int((tgw_ulx - self.ulx) / self.pixel_width)
        sw_yoff = int((tgw_uly - self.uly) / self.pixel_height)
        sw_xsize = int((tgw_lrx - self.ulx) / self.pixel_width + 0.5) - sw_xoff
        sw_ysize = int((tgw_lry - self.uly) / self.pixel_height + 0.5) - sw_yoff

        if sw_xsize < 1 or sw_ysize < 1:
            return 1

        # Open the source file, and copy the selected region.
        source_file = gdal.Open(self.filename)

        source_band = source_file.GetRasterBand(source_band)
        target_band = output_file.GetRasterBand(target_band)

        data = source_band.ReadRaster(sw_xoff, sw_yoff, sw_xsize, sw_ysize,
                                      tw_xsize, tw_ysize, target_band.DataType)
        target_band.WriteRaster(tw_xoff, tw_yoff, tw_xsize, tw_ysize,
                                data, tw_xsize, tw_ysize, target_band.DataType)

        del source_file

        return 1
