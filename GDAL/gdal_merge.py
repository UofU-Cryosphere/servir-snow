import click
import fnmatch
import glob
import os
import shutil
import sys

from gdal_calc import gdal_calc
from osgeo import gdal, osr
from lib import TileFile

OUTPUT_FORMAT = 'GTiff'


def ensure_slash(value):
    if not value.endswith('/'):
        return value + '/'
    else:
        return value


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


def doy_from_file_name(filename):
    return filename.split('.')[1][1:]


def move_files_to_folder(file, doys, source_folder):
    for doy in doys:
        source_folder_for_file = ensure_slash(source_folder + doy)
        if not os.path.exists(source_folder_for_file):
            os.mkdir(source_folder_for_file)

        if fnmatch.fnmatch(file, '*' + doy + '*'):
            shutil.move(file, source_folder_for_file)
            return


def days_to_process(files):
    days = set()

    [days.add(doy_from_file_name(filename)) for filename in files]

    return days


def merge_tiles(source_folder):
    out_file = output_file_name + '.tif'

    # Remove old output file
    if os.path.isfile(out_file):
        os.remove(out_file)

    file_queue = []
    ulx, uly, lrx, lry = 0.0, 0.0, 0.0, 0.0
    gdal_driver = gdal.GetDriverByName(OUTPUT_FORMAT)

    for file in glob.glob(source_folder + '*[!_proj,_rf].tif'):
        file = TileFile(file)
        file_queue.append(file)
        # Remember dimensions for output file
        if ulx == 0.0:
            ulx = file.ulx
        else:
            ulx = min(ulx, file.ulx)
        uly = max(uly, file.uly)
        lrx = max(lrx, file.lrx)
        if lry == 0.0:
            lry = file.lry
        else:
            lry = min(lry, file.lry)

    pixel_width = file_queue[0].pixel_width
    pixel_height = file_queue[0].pixel_height

    bands = file_queue[0].bands
    band_type = file_queue[0].band_type

    geotransform = [ulx, pixel_width, 0, uly, 0, pixel_height]
    xsize = int((lrx - ulx) / pixel_width + 0.5)
    ysize = int((lry - uly) / pixel_height + 0.5)

    output_file = gdal_driver.Create(out_file, xsize, ysize, bands, band_type)

    output_file.SetGeoTransform(geotransform)
    output_file.SetProjection(file_queue[0].projection)

    fi_processed = 0

    # Copy data from source files into output file.
    bands_to_copy = range(1, bands+1)
    for file in file_queue:

        print("Processing file %4d of %4d, %6.3f%% completed"
              % (fi_processed+1, len(file_queue),
                 fi_processed * 100.0 / len(file_queue)))
        # file.report()

        [file.copy_into(output_file, band, band) for band in bands_to_copy]

        fi_processed = fi_processed + 1

        del file

    del output_file


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
    source_folder = ensure_slash(kwargs['source_folder'])

    if 'scan_folder' in kwargs and kwargs['scan_folder'] is True:
        print('Scanning folder for newly downloaded files')

        files = glob.glob(source_folder + '*.tif')
        days = sorted(days_to_process(files))

        [
            move_files_to_folder(file, days, source_folder)
            for file in files
        ]

    doys = glob.glob(source_folder + '20[0,1,2][0-9]*')

    for doy_folder in doys:
        print('Processing folder: ' + doy_folder)
        file_name = os.path.basename(doy_folder)
        doy_folder = ensure_slash(doy_folder)
        output_file_name = doy_folder + file_name

        merge_tiles(doy_folder)

        filter_band_values(kwargs['band_threshold'])

        warp()

    print('Done processing source folder')


if __name__ == '__main__':
    sys.exit(process_folder())
