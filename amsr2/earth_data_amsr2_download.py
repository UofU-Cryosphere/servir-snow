#!/usr/bin/python

from multiprocessing import Pool

import click

from lib import EarthData
from lib.download_utils import download_file


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
def data_download(**kwargs):
    session = EarthData(kwargs['username'], kwargs['password'], 'AMSR2')
    file_list = session.list_datafiles()
    p = Pool(4)
    p_res = [
        p.apply_async(
            download_file,
            (session, name, url, kwargs['download_folder'])
        ) for name, url in file_list.items()
    ]
    [res.get() for res in p_res]


if __name__ == '__main__':
    data_download()
