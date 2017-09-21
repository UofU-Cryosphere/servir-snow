#!/usr/bin/python

import os
import click

from multiprocessing import Pool
from lib import EarthData


def download_file(session, name, url, download_folder):
    file_size = int(session.head(url).headers['Content-Length'])
    file_name = download_folder + name

    if not os.path.isfile(file_name) or os.path.getsize(file_name) != file_size:
        response = session.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=2000000):
                f.write(chunk)
        if response.status_code is 200:
            print('Successfully downloaded:' + file_name)
        else:
            print('Download for:' + file_name + ' failed')
    else:
        print('File:' + file_name + ' already downloaded')


def ensure_slash(_ctx, _param, value):
    if not value.endswith('/'):
        return value + '/'
    else:
        return value


@click.command()
@click.option('--username',
              prompt='Your username',
              help='Your EartData username')
@click.password_option(confirmation_prompt=False,
                       help='Your EarthData password')
@click.option('--download-folder',
              type=click.Path(exists=True),
              prompt=True,
              callback=ensure_slash,
              help='The destination folder to store the files')
def data_download(**kwargs):
    session = EarthData(kwargs['username'], kwargs['password'])
    file_list = session.list_datafiles('AMSR2')
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
