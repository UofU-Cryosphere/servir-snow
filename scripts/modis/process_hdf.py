#!/usr/bin/python
import os
import sys

import click
from osgeo import gdal

from snowrs import SourceFolder, ReferenceInfo
from snowrs.script_helpers import parse_year

GDAL_MEM = gdal.GetDriverByName('MEM')
GDAL_TIFF = gdal.GetDriverByName('GTiff')

GDAL_OPTIONS = ["COMPRESS=LZW", "TILED=YES",
                "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]

OUTPUT_FILE_SUFFIX = '_{0}.tif'


@click.command()
@click.option('--source-folder',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of source files')
@click.option('--tmp-folder',
              prompt=True,
              type=click.Path(exists=True),
              help='Location for tmp files')
@click.option('--reference-file',
              prompt=True,
              type=click.Path(exists=True),
              help='Location for tmp files')
@click.option('--year',
              prompt=False,
              type=int,
              callback=parse_year,
              help='Optional - Process specific year')
def process_folder(**kwargs):
    source_folder = SourceFolder(
        kwargs['source_folder'], source_file_type='*.h5'
    )
    reference = ReferenceInfo(kwargs['reference_file'])

    for year in kwargs['year']:
        print('Processing year: ' + str(year))
        source_folder.year = year

        if not os.path.exists(source_folder.type_path):
            print('* No path found for year: {0} *\n'.format(year))
            continue

        for file in source_folder.files:
            source = gdal.Open(file)

            print('Processing file:\n   {0} \n'.format(file))

            for index, layer in enumerate(source.GetSubDatasets()):
                layer_file = GDAL_MEM.CreateCopy('', gdal.Open(layer[0]), 0)
                reference.copy_to_file(layer_file)

                layer_file = gdal.Warp(
                    '', layer_file, dstSRS='EPSG:4326', format='MEM'
                )

                output_file_name = source.GetDescription()
                output_file_name = output_file_name.replace(
                    '.h5', OUTPUT_FILE_SUFFIX.format(layer[0].split('/')[-1])
                )
                GDAL_TIFF.CreateCopy(
                    output_file_name, layer_file, strict=0, options=GDAL_OPTIONS
                )

                del layer_file


if __name__ == '__main__':
    sys.exit(process_folder())
