#!/usr/bin/python

import os
from multiprocessing import Pool

import click

from lib import JPLData
from lib import SourceFolder
from lib.download_utils import download_file
from modis.script_helpers import parse_year


def to_array(_ctx, _param, value):
    return value.split(',')


def validate_type(ctx, _param, value):
    if value not in JPLData.TYPES:
        print('Invalid data type')
        ctx.abort()
    else:
        return value


def get_from_jpl(username, password, name, url, download_folder):
    session = JPLData(username, password)
    return download_file(session, name, url, download_folder)


@click.command()
@click.option('--username',
              prompt='Your username',
              help='Your EarthData username')
@click.password_option(confirmation_prompt=False,
                       help='Your EarthData password')
@click.option('--download-folder',
              type=click.Path(exists=True),
              prompt=True,
              help='The destination folder to store the files')
@click.option('--year',
              prompt=False,
              type=int,
              callback=parse_year,
              help='The year (YYYY) to download data from.'
                   'Leave blank to download all data starting from 2000')
@click.option('--day-from',
              prompt=True,
              type=int,
              help='The starting day to download data from')
@click.option('--day-to',
              prompt=True,
              type=int,
              help='The ending day to download data from')
@click.option('--source-type',
              prompt='The type of data - fraction or forcing',
              callback=validate_type,
              help='The type of data - fraction or forcing')
@click.option('--tiles',
              prompt=True,
              callback=to_array,
              help='List of tiles separated by comma (,)')
@click.option('--file-names',
              prompt=True,
              callback=to_array,
              help='Pattern of file to look for')
def data_download(**kwargs):
    session = JPLData(kwargs['username'], kwargs['password'])
    # To authenticate for the session
    session.get_index(kwargs['source_type'])

    days = range(kwargs['day_from'], kwargs['day_to'] + 1)

    source_folder = SourceFolder(
        base_path=kwargs['download_folder'],
        source_type=kwargs['source_type']
    )

    for year in kwargs['year']:
        print('Processing year: ' + str(year))
        source_folder.year = year

        download_folder = source_folder.type_path

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        print('Downloading files: ' + ', '.join(kwargs['file_names']) +
              '\n for tiles: ' + ', '.join(kwargs['tiles']) +
              '\n in day range ' + str(kwargs['day_from']) +
              ' to ' + str(kwargs['day_to']))

        file_list = session.files_for_date_range(
            kwargs['source_type'],
            kwargs['tiles'],
            year,
            days,
            kwargs['file_names'],
        )

        print('Found ' + str(len(file_list)) + ' files to download')
        p = Pool(4)
        p_res = [
            p.apply_async(
                get_from_jpl,
                (kwargs['username'], kwargs['password'], name, url, download_folder)
            ) for name, url in file_list.items()
        ]
        [res.get() for res in p_res]


if __name__ == '__main__':
    data_download()
