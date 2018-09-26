#!/usr/bin/python

import os
from multiprocessing import Pool

import click

from snowrs import EarthData
from snowrs.script_helpers import dates_in_range, download_file


# TODO - Remove me
def ensure_folder(folder):
    if not (os.path.isdir(folder)):
        os.mkdir(folder)

    return folder


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
    session = EarthData(kwargs['username'], kwargs['password'], 'AMSRE')
    # To authenticate for the session
    session.get_index()

    dates = dates_in_range(kwargs['year'], kwargs['day_from'], kwargs['day_to'])
    download_folder = ensure_folder(
        os.path.join(kwargs['download_folder'], str(kwargs['year']))
    )
    file_list = session.files_for_date_range(dates)

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
