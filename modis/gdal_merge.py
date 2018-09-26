import os
import sys

import click

from lib import SourceFolder, TileMerger
from modis.script_helpers import parse_year, validate_types


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
    source_type = kwargs['source_type']
    source_folder = SourceFolder(kwargs['source_folder'], source_type)

    for year in kwargs['year']:
        print('Processing year: ' + str(year))
        source_folder.year = year

        if not os.path.exists(source_folder.type_path):
            print('* No path found for year: {0} *\n'.format(year))
            continue

        if 'scan_folder' in kwargs and kwargs['scan_folder'] is True:
            print('* Scanning folder for new files and move to folder:\n')
            print('  {0}'.format(source_folder.type_path))
            source_folder.process_new_files()

        for doy_folder in source_folder.doy_folders():
            print('  Processing folder: ' + doy_folder)

            merger = TileMerger(
                doy_folder,
                source_type
            )

            if merger.create_mosaic() == -1:
                continue

            merger.project()

            del merger

            print('Done processing source folder: ' + source_folder.type_path)


if __name__ == '__main__':
    sys.exit(process_folder())
