from osgeo import gdal, gdalnumeric, osr

import numpy
import os

# Utility script to setup tests sources.
# Creates four tests files that together form a L-shaped mosaic output
#  _____
# |x|x|x|
# ----|x|
#
# Each file will have some extreme values that will get filtered based on image
# type. See lib/tile_file.py for threshold values.
# Each file will be 3x3 pixels, creating a 9x6 output file.
#
# For help on forcing values: https://snow.jpl.nasa.gov/portal/data/help_modscag

TILES = {
    'upper_left.tif': numpy.array([[-999, 0, 0], [10, 20, 100], [100, 2450, 2450]]),
    'middle.tif': numpy.array([[-999, 0, 0], [10, 200, 400], [400, 2500, 2500]]),
    'upper_right.tif': numpy.array([[-999, 0, 0], [10, 800, 900], [-10, 2550, 2550]]),
    'bottom_right.tif': numpy.array([[-999, 0, 0], [-10, -20, 20], [10, 2300, 2300]]),
}
geo_transform = {
    'upper_left.tif': [0, 1, 0, 6, 0, -1],
    'middle.tif': [3, 1, 0, 6, 0, -1],
    'upper_right.tif': [6, 1, 0, 6, 0, -1],
    'bottom_right.tif': [6, 1, 0, 3, 0, -1],
}
tile_x = 3
tile_y = 3
tile_bands = 1

projection = osr.SpatialReference()
projection.ImportFromEPSG(4326)

source_folder = 'source_tiffs'
source_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    source_folder
)

if not os.path.exists(source_path):
    os.mkdir(source_path)


OUTPUT_FORMAT = 'GTiff'
gdal_driver = gdal.GetDriverByName(OUTPUT_FORMAT)


for tile_name, tile_values in TILES.items():
    output_file_name = os.path.join(source_folder, tile_name)

    if os.path.isfile(output_file_name):
        os.remove(output_file_name)

    output_file = gdal_driver.Create(
        output_file_name,
        tile_x, tile_y,
        tile_bands,
        gdal.GDT_Int16  # Int16 to enable NoData value of -999
    )

    output_file.SetGeoTransform(geo_transform[tile_name])
    output_file.SetProjection(projection.ExportToWkt())

    target_band = output_file.GetRasterBand(tile_bands)
    target_band.SetNoDataValue(2550) # From MODSCAG spec
    gdalnumeric.BandWriteArray(target_band, tile_values)

    del target_band
    del output_file
