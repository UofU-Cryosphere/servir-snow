import os

from osgeo import gdal, gdalconst, gdalnumeric, osr
from pyproj import Proj, transform


class SWE:
    SOURCE_SPAT_RES = 25000  # In Meters

    BAND_MAX_DATA_VALUE = 240
    BAND_VALUE_SCALE_FACTOR = 2

    NO_DATA_VALUE = -999

    NSIDC_EASE_GRID_NORTH = osr.SpatialReference()
    NSIDC_EASE_GRID_NORTH.ImportFromEPSG(3408)
    NSIDC_EASE_GRID_NORTH_PROJ = Proj(NSIDC_EASE_GRID_NORTH.ExportToProj4())
    NSIDC_NORTH_UL_X, NSIDC_NORTH_UL_Y = transform(
        Proj(init='epsg:4326'),
        NSIDC_EASE_GRID_NORTH_PROJ,
        -135,  # These are approximate degree values
        -86.5  # Source: NSIDC
    )

    GDAL_DRIVER_TYPE = 'MEM'
    GDAL_DRIVER = gdal.GetDriverByName(GDAL_DRIVER_TYPE)

    def __init__(self, hdf_file_name):
        self._hdf_file_name = hdf_file_name
        self._file_dir = os.path.dirname(hdf_file_name)
        self._hdf_file = None
        self._tif_file = None

    @property
    def hdf_file(self):
        if self._hdf_file is None:
            self._hdf_file = gdal.Open(
                self._hdf_file_name, gdalconst.GA_ReadOnly
            )
        return self._hdf_file

    @property
    def tif_file(self):
        return self._tif_file

    def northern_swe(self):
        """
        Read northern hemisphere SWE data and filter all values above 240 and
        scale values by factor 2.

        Data Parameters description:
        https://lance.nsstc.nasa.gov/amsr2-science/doc/LANCE_A2_DySno_NRT_dataset.pdf

        :return: Numpy array with SWE values
        """
        northern_swe = self.hdf_file.GetSubDatasets()[0]

        northern_swe = gdal.Open(northern_swe[0], gdalconst.GA_ReadOnly)
        northern_swe = northern_swe.ReadAsArray(buf_type=gdalconst.GDT_Int16)

        northern_swe[
            northern_swe > self.BAND_MAX_DATA_VALUE
            ] = self.NO_DATA_VALUE
        northern_swe[
            northern_swe > self.NO_DATA_VALUE
            ] *= self.BAND_VALUE_SCALE_FACTOR

        return northern_swe

    def __hdf_to_tif(self):
        data = self.northern_swe()

        self._tif_file = self.GDAL_DRIVER.Create(
            os.path.join(self._file_dir, 'North_SWE_25k_nsidc.tif'),
            data.shape[1], data.shape[0],
            1, gdalconst.GDT_Int16,
        )
        self.tif_file.SetGeoTransform(
            [self.NSIDC_NORTH_UL_X, self.SOURCE_SPAT_RES, 0,
             self.NSIDC_NORTH_UL_Y, 0, -self.SOURCE_SPAT_RES]
        )
        self.tif_file.SetProjection(self.NSIDC_EASE_GRID_NORTH.ExportToWkt())

        band = self.tif_file.GetRasterBand(1)
        band.SetNoDataValue(self.NO_DATA_VALUE)
        gdalnumeric.BandWriteArray(band, data)

        band.FlushCache()

        del data
        del band

    def __project(self, projection):
        self._tif_file = gdal.Warp(
            os.path.join(self._file_dir, 'North_SWE_25k_warp.tif'),
            self.tif_file,
            format=self.GDAL_DRIVER_TYPE,
            dstSRS=projection,
        )

    def clip_to_tif(self, reference_file):
        """
        Method converts initialized HDF file to a GeoTiff with data from the
        northern hemisphere. Given tif_file is used to transform the HDF file to
        identical extent, resolution, and projection

        :param reference_file: Reference GeoTiff file
        """
        self.__hdf_to_tif()
        self.__project(reference_file.GetProjection())
        geo_transform = reference_file.GetGeoTransform()

        ul_x = geo_transform[0]
        ul_y = geo_transform[3]
        lr_x = ul_x + geo_transform[1] * reference_file.RasterXSize
        lr_y = ul_y + geo_transform[5] * reference_file.RasterYSize

        self._tif_file = gdal.Translate(
            os.path.join(self._file_dir, 'North_SWE_clip.tif'),
            self.tif_file,
            xRes=geo_transform[1], yRes=geo_transform[5],
            projWin=[ul_x, ul_y, lr_x, lr_y],
            projWinSRS=reference_file.GetProjection(),
            outputSRS=reference_file.GetProjection(),
            format=self.GDAL_DRIVER_TYPE,
            resampleAlg=gdalconst.GRA_Bilinear,
        )
