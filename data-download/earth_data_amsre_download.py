#!/usr/bin/python

import click

from multiprocessing import Pool
from lib import EarthData
from lib.download_utils import *


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
              prompt=True,
              type=int,
              help='The year (YYYY) to download data from')
@click.option('--day-from',
              prompt=True,
              type=int,
              help='The starting day to download data from')
@click.option('--day-to',
              prompt=True,
              type=int,
              help='The ending day to download data from')
def data_download(**kwargs):
    session = EarthData(kwargs['username'], kwargs['password'])
    # To authenticate for the session
    session.get_index('AMSRE')

    dates = dates_in_range(kwargs['year'], kwargs['day_from'], kwargs['day_to'])
    download_folder = ensure_folder(
        kwargs['download_folder'] + '/' + str(kwargs['year'])
    )
    file_list = session.files_for_date_range('AMSRE', dates)

    p = Pool(4)
    p_res = [
        p.apply_async(
            download_file,
            (session, name, url, download_folder)
        ) for name, url in file_list.items()
    ]
    [res.get() for res in p_res]


if __name__ == '__main__':
    data_download()
