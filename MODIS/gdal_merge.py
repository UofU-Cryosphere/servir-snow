import datetime
import os
import sys

import click

from lib import SourceFolder, TileMerger

FILTER_TYPES = {
    'forcing': {
        'source_folder': 'forcing',
        'file_suffix': '_rf.tif'
    },
    'fraction': {
        'source_folder': 'snow_fraction',
        'file_suffix': '_SCA.tif'
    }
}


def validate_types(ctx, _param, value):
    if value not in FILTER_TYPES:
        print('Invalid source data type\n' +
              'Possible options:\n' +
              ' * forcing\n' +
              ' * fraction')
        ctx.abort()
    else:
        return value


def parse_year(_ctx, _param, value):
    if value:
        return range(value, value + 1)
    else:
        return range(2000, datetime.date.today().year + 1)


@click.command()
@click.option('--source-folder',
              prompt=True,
              type=click.Path(exists=True),
              help='Location of source files')
@click.option('--source-type',
              prompt=True,
              callback=validate_types,
              help='Type of data')
@click.option('--year',
              prompt=False,
              type=int,
              callback=parse_year,
              help='Optional - Process specific year')
@click.option('--scan-folder',
              is_flag=True,
              help='Scan the source folder for newly downloaded files')
def process_folder(**kwargs):
    global output_file_name
    global source_type

    source_type = kwargs['source_type']

    for year in kwargs['year']:

        source_path = os.path.join(kwargs['source_folder'],
                                   str(year),
                                   FILTER_TYPES[source_type]['source_folder'])

        if not os.path.exists(source_path):
            continue

        source_folder = SourceFolder(source_path)

        print('Processing year: ' + str(year))

        if 'scan_folder' in kwargs and kwargs['scan_folder'] is True:
            print('Scanning folder for newly downloaded files')
            source_folder.scan_for_new_files()

        for doy_folder in source_folder.get_folders_to_process():
            print('Processing folder: ' + doy_folder)
            file_name = os.path.basename(os.path.dirname(doy_folder))
            output_file_name = \
                doy_folder + file_name + FILTER_TYPES[source_type]['file_suffix']

            merger = TileMerger(
                doy_folder,
                output_file_name,
                source_type
            )

            if merger.create_mosaic() == -1:
                continue

            merger.project()

            del merger

            print('Done processing source folder: ' + source_path)


if __name__ == '__main__':
    sys.exit(process_folder())
