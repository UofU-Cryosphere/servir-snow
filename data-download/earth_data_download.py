#!/usr/bin/python

import requests
import re
import os
import click

from bs4 import BeautifulSoup
from multiprocessing import Pool


class EarthData(requests.Session):
    SOURCES = {
        'AMSR2': 'https://lance.nsstc.nasa.gov/amsr2-science/data/level3/daysnow/R00/hdfeos5/'
    }

    FILE_REGEX = {
        'AMSR2': 'AMSR_2_L3_DailySnow_.*'
    }

    def __init__(self, username, password):
        super(EarthData, self).__init__()
        self.auth = (username, password)

    def get_index(self, source):
        return self.get(self.SOURCES[source])

    def list_datafiles(self, source):
        files = BeautifulSoup(self.get_index(source).text, 'html.parser')
        links = files.find_all(href=re.compile(self.FILE_REGEX[source]))
        list = {
            link.attrs['href']: self.SOURCES[source] + link.attrs['href']
            for link in links if link is not None
        }

        return list


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


def ensure_slash(ctx, param, value):
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
