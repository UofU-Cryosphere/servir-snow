import requests
import re

from bs4 import BeautifulSoup


class EarthData(requests.Session):
    SOURCES = {
        'AMSR2': 'https://lance.nsstc.nasa.gov/amsr2-science/data/level3/daysnow/R00/hdfeos5/',
    }

    FILE_REGEX = {
        'AMSR2': 'AMSR_2_L3_DailySnow_.*',
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
