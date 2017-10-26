import click
import glob
import tables
import os
import sys

from osgeo.gdalnumeric import *
from pyproj import Proj, transform

import nsidc

# pixel spatial resolution in meters
SPAT_RES = 25000
INPUT_PROJECTION = Proj(init='epsg:4326')

NORTH_SWE = '/HDFEOS/GRIDS/Northern Hemisphere/Data Fields/SWE_NorthernDaily'
SOUTH_SWE = '/HDFEOS/GRIDS/Southern Hemisphere/Data Fields/SWE_SouthernDaily'

FILE_ENDING = '.he5'
NORTH_SWE_FILE = 'North_SWE' + FILE_ENDING

BAND_THRESHOLD = 240


def get_file_data(file):
    h5file = tables.open_file(file)
    north_grid_swe = h5file.get_node(NORTH_SWE).read()
    h5file.close()

    # Filter all values above threshold
    north_grid_swe[north_grid_swe > BAND_THRESHOLD] = 0
    # Double remaining values
    north_grid_swe *= 2

    return north_grid_swe


def convert_file(infile):
    output_file = os.path.basename(infile).split('.')[0] + '_' + NORTH_SWE_FILE
    output_file = os.path.join(os.path.dirname(infile), output_file)
    if os.path.isfile(output_file):
        return 1

    tiff_data = get_file_data(infile)

    gdal_driver = gdal.GetDriverByName("GTiff")

    # Converts coordinates from WGS 1984 to polar grid coordinates
    ul_x, ul_y = transform(
        INPUT_PROJECTION,
        nsidc.NORTH_PROJ,
        nsidc.NORTH_UL_LON,
        nsidc.NORTH_UL_LAT
    )

    output_file = gdal_driver.Create(
        output_file,
        tiff_data.shape[1],
        tiff_data.shape[0],
        1,
        gdal.GDT_Byte
    )
    output_file.SetGeoTransform([ul_x, SPAT_RES, 0, ul_y, 0, -SPAT_RES])
    output_file.SetProjection(nsidc.NORTH_PROJECTION)

    # Write gridded swath to the output file
    output_band = output_file.GetRasterBand(1)
    BandWriteArray(output_band, tiff_data)

    output_file = None
    output_band = None


@click.command()
@click.option('--source-folder',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of source files')
def process_folder(**kwargs):
    file_pattern = os.path.join(kwargs['source_folder'], '*' + FILE_ENDING)
    for file in glob.glob(file_pattern):
        _filename = os.path.basename(file)

        if _filename.endswith(NORTH_SWE_FILE):
            continue

        print('Processing file: ' + _filename)
        convert_file(file)


if __name__ == '__main__':
    sys.exit(process_folder())
