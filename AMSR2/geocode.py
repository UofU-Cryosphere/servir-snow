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


def convert_file(infile):
    output_file = os.path.basename(infile).split('.')[0] + '_' + NORTH_SWE_FILE
    output_file = os.path.dirname(infile) + '/' + output_file
    if os.path.isfile(output_file):
        return 1

    h5file = tables.open_file(infile)
    north_grid_swe = h5file.get_node(NORTH_SWE).read()
    h5file.close()

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
        north_grid_swe.shape[1],
        north_grid_swe.shape[0],
        1,
        gdal.GDT_Byte
    )
    output_file.SetGeoTransform([ul_x, SPAT_RES, 0, ul_y, 0, -SPAT_RES])
    output_file.SetProjection(nsidc.NORTH_PROJECTION)

    # Write gridded swath to the output file
    output_band = output_file.GetRasterBand(1)
    BandWriteArray(output_band, north_grid_swe)

    output_file = None
    output_band = None


def ensure_slash(_ctx, _param, value):
    if not value.endswith('/'):
        return value + '/'
    else:
        return value


@click.command()
@click.option('--source-folder',
              prompt=True,
              type=click.Path(exists=True),
              callback=ensure_slash,
              help='Location of source files')
def process_folder(**kwargs):
    for file in glob.glob(kwargs['source_folder'] + '*' + FILE_ENDING):
        _filename = os.path.basename(file)

        if _filename.endswith(NORTH_SWE_FILE):
            continue

        print('Processing file: ' + _filename)
        convert_file(file)


if __name__ == '__main__':
    sys.exit(process_folder())
