import os
import sys

import click

from snowrs import Composite, SourceFolder
from snowrs.script_helpers import parse_year, validate_types


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
@click.option('--day',
              prompt=False,
              type=int,
              help='Optional - Process specific day of year')
def process_folder(**kwargs):
    source_folder = SourceFolder(
        kwargs.pop('source_folder'), kwargs['source_type']
    )

    for year in kwargs.pop('year'):
        source_folder.year = year

        if not os.path.exists(source_folder.type_path):
            print('* No path found for year: {0} *\n'.format(year))
            continue

        comp = Composite(
            year=year, source_folder=source_folder.type_path, **kwargs
        )
        if kwargs['day']:
            comp.create_for_day(kwargs['day'])
        else:
            comp.create()


if __name__ == '__main__':
    sys.exit(process_folder())
