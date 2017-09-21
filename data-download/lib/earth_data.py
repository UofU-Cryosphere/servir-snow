import requests
import re

from bs4 import BeautifulSoup


class EarthData(requests.Session):
    SOURCES = {
        'AMSR2': 'https://lance.nsstc.nasa.gov/amsr2-science/data/level3/daysnow/R00/hdfeos5/',
        'AMSRE': 'https://n5eil01u.ecs.nsidc.org/AMSA/AE_DySno.002/',
    }

    FILE_REGEX = {
        'AMSR2': re.compile('AMSR_2_L3_DailySnow_.*'),
        'AMSRE': re.compile('AMSR_E_L3_DailySnow_V[\d]{2}_.*[.]hdf$'),
    }

    def __init__(self, username, password):
        super(EarthData, self).__init__()
        self.auth = (username, password)

    def get_index(self, source):
        return self.get(self.SOURCES[source])

    # For data sources that have each day in a separate folder
    def files_for_date_range(self, source, date_range):
        files = {}

        for date in date_range:
            folder_name = date.strftime("%Y.%m.%d")
            index_dir_url = self.SOURCES[source] + folder_name + '/'
            dir_index = BeautifulSoup(self.get(index_dir_url).text, 'html.parser')
            file_link = dir_index.find('a', text=self.FILE_REGEX[source])
            files[file_link.attrs['href']] =\
                index_dir_url + file_link.attrs['href']

        return files

    # For data sources that have all files in one directory
    def list_datafiles(self, source):
        files = BeautifulSoup(self.get_index(source).text, 'html.parser')
        links = files.find_all(href=self.FILE_REGEX[source])
        return {
            link.attrs['href']: self.SOURCES[source] + link.attrs['href']
            for link in links if link is not None
        }
