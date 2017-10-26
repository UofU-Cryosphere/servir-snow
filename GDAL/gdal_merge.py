import click
import os
import sys

from gdal_calc import gdal_calc
from osgeo import gdal, osr
from lib import SourceFolder, TileMerger

OUTPUT_FORMAT = 'GTiff'


def warp():
    source = gdal.Open(output_file_name + '_rf.tif')
    output_file = output_file_name + '_rf_proj.tif'

    print('Generating projected output file: ' + output_file)

    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(4326)

    # Call AutoCreateWarpedVRT() to fetch default values for target
    # raster dimensions and geotransform
    tmp_ds = gdal.AutoCreateWarpedVRT(source,
                                      None,  # src_wkt : left to default value
                                      dst_srs.ExportToWkt(),
                                      gdal.GRA_NearestNeighbour,
                                      0.125  # same value as in gdalwarp
                                      )

    file = gdal.GetDriverByName(OUTPUT_FORMAT).CreateCopy(output_file, tmp_ds)
    file = None


def filter_band_values(threshold_value):
    source_file = output_file_name + '.tif'
    output_file = output_file_name + '_rf.tif'
    gdal_calc(source_file, output_file, threshold_value)


@click.command()
@click.option('--source-folder',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of source files')
@click.option('--band-threshold',
              prompt=True,
              type=int,
              help='Band threshold to filter values above')
@click.option('--scan-folder',
              type=bool,
              default=False,
              help='Scan the source folder for newly downloaded files')
def process_folder(**kwargs):
    global output_file_name

    source_folder = SourceFolder(kwargs['source_folder'])

    if 'scan_folder' in kwargs and kwargs['scan_folder'] is True:
        print('Scanning folder for newly downloaded files')
        source_folder.scan_for_new_files()

    for doy_folder in source_folder.get_folders_to_process():
        print('Processing folder: ' + doy_folder)
        file_name = os.path.basename(os.path.dirname(doy_folder))
        output_file_name = doy_folder + file_name

        TileMerger(doy_folder, output_file_name).create_mosaic()

        filter_band_values(kwargs['band_threshold'])

        warp()

    print('Done processing source folder')


if __name__ == '__main__':
    sys.exit(process_folder())
