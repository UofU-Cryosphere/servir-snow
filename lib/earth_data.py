import re

import requests
from bs4 import BeautifulSoup
from requests.compat import urlparse


class EarthData(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    SOURCES = {
        'AMSR2': 'https://lance.nsstc.nasa.gov/' +
                 'amsr2-science/data/level3/daysnow/R00/hdfeos5/',
        'AMSRE': 'https://n5eil01u.ecs.nsidc.org/AMSA/AE_DySno.002/',
    }

    FILE_REGEX = {
        'AMSR2': re.compile('AMSR_2_L3_DailySnow_.*'),
        'AMSRE': re.compile('AMSR_E_L3_DailySnow_V[\d]{2}_.*[.]hdf$'),
    }

    def __init__(self, username, password, source):
        super(EarthData, self).__init__()
        self.auth = (username, password)
        self.source = source

    # Overrides from the library to keep headers when redirected to or from
    # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = urlparse(response.request.url)
            redirect_parsed = urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']

        return

    def get_index(self):
        return self.get(self.SOURCES[self.source])

    # For data sources that have each day in a separate folder
    def files_for_date_range(self, date_range):
        files = {}

        for date in date_range:
            folder_name = date.strftime("%Y.%m.%d")
            index_dir_url = self.SOURCES[self.source] + folder_name + '/'
            dir_index = BeautifulSoup(self.get(index_dir_url).text, 'html.parser')
            file_link = dir_index.find('a', text=self.FILE_REGEX[self.source])
            files[file_link.attrs['href']] =\
                index_dir_url + file_link.attrs['href']

        return files

    # For data sources that have all files in one directory
    def list_datafiles(self):
        files = BeautifulSoup(self.get_index().text, 'html.parser')
        links = files.find_all(href=self.FILE_REGEX[self.source])
        return {
            link.attrs['href']: self.SOURCES[self.source] + link.attrs['href']
            for link in links if link is not None
        }
