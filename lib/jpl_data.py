import re

import requests
from bs4 import BeautifulSoup


class JPLData(requests.Session):
    BASE_URL = 'https://snow-data.jpl.nasa.gov'
    ARCHIVE_PATH = '-historic'
    TYPES = {
        'fraction': BASE_URL + '/modscag',
        'forcing': BASE_URL + '/moddrfs'
    }

    FILE_BASE_REGEX = 'MOD09GA[.]A[\d]{7}[.]'

    def __init__(self, **kwargs):
        super(JPLData, self).__init__()
        self.auth = requests.auth.HTTPDigestAuth(
            kwargs['username'], kwargs['password']
        )
        self._source_type = kwargs['source_type']

    @property
    def source_type(self):
        return self._source_type

    def requested_files_regex(self, tiles, file_types):
        regex = '(' + '|'.join(tiles) + ').*(' + '|'.join(file_types) + ')$'
        return re.compile(self.FILE_BASE_REGEX + regex, re.IGNORECASE)

    def __get_index_url(self, year, day):
        url = self.TYPES[self.source_type]
        if year < 2015:
            url += self.ARCHIVE_PATH
        url += '/' + str(year) + '/' + day + '/'

        return url

    def files_for_date_range(self, tiles, year, day_range, file_types):
        files = {}

        for day in day_range:
            print('Parsing download links for day: ' + str(day))
            day = str(day).rjust(3, '0')

            index_dir_url = self.__get_index_url(year, day)
            file_links = BeautifulSoup(
                self.get(index_dir_url).text, 'html.parser'
            ).find_all(
                'a', text=self.requested_files_regex(tiles, file_types)
            )

            [
                files.update({link.text: index_dir_url + link.attrs['href']})
                for link in file_links
            ]

        return files
