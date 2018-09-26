import os
import sys
from datetime import date, timedelta

import numpy as np
from osgeo import gdal
from osgeo import gdalnumeric

from .tile_merger import TileMerger


class Composite(object):
    NUMBER_OF_DAYS = 8
    START_DAY_OF_WEEK = 1  # Sunday

    COMPOSITE_OUTPUT_FOLDER = 'composites'
    COMPOSITE_FILE_SUFFIX = '_{1}_days{0}'

    SINGLE_DAY_NAME = '{0}{1}'

    GDAL_DRIVER = gdal.GetDriverByName('GTiff')
    GDAL_OPTIONS = ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=IF_SAFER"]

    def __init__(self, **kwargs):
        self._composite_folder = None
        self._source_folder = os.path.join(kwargs['source_folder'], '')
        self._source_type = kwargs['source_type']
        self._year = kwargs['year']
        self._number_of_days = kwargs.get('number_of_days', self.NUMBER_OF_DAYS)
        self._start_day_of_week = kwargs.get(
            'start_day_of_week', self.START_DAY_OF_WEEK
        )

    @property
    def composite_folder(self):
        if self._composite_folder is None:
            self._composite_folder = os.path.join(
                self.source_folder, self.COMPOSITE_OUTPUT_FOLDER, ''
            )

            if not os.path.exists(self._composite_folder):
                os.mkdir(self._composite_folder)
        return self._composite_folder

    @property
    def number_of_days(self):
        return self._number_of_days

    @property
    def start_day_of_week(self):
        return self._start_day_of_week

    @property
    def source_folder(self):
        return self._source_folder

    @property
    def source_type(self):
        return self._source_type

    @property
    def year(self):
        return self._year

    def start_days_in_year(self):
        start_days_in_year = []

        first_day_of_year = date(self.year, 1, 1)
        day_of_year = first_day_of_year + timedelta(
            days=(6 - first_day_of_year.weekday())
        )

        while day_of_year.year == self.year:
            start_days_in_year.append(day_of_year.timetuple().tm_yday)
            day_of_year += timedelta(days=self.number_of_days - 1)

        return start_days_in_year

    def single_day(self, day_number):
        return self.SINGLE_DAY_NAME.format(
            self.year, str(day_number).rjust(3, '0')
        )

    def single_day_input_file(self, day_number):
        return os.path.join(
            self.source_folder,
            self.single_day(day_number),
            self.SINGLE_DAY_NAME.format(
                self.single_day(day_number),
                TileMerger.FILE_SUFFIX[self.source_type]
            ),
        )

    def file_name(self, day):
        return os.path.join(
            self.composite_folder,
            self.single_day(day) +
            self.COMPOSITE_FILE_SUFFIX.format(
                TileMerger.FILE_SUFFIX[self.source_type], self.number_of_days
            )
        )

    def create_for_day(self, start_day):
        week = []
        file_for_copy = None
        no_data_value = None

        for day in range(0, self.NUMBER_OF_DAYS):
            file_path = self.single_day_input_file(start_day + day)

            if not os.path.exists(file_path):
                continue

            print('  Reading file: \n    {0}'.format(file_path))
            file = gdal.Open(file_path)
            band = file.GetRasterBand(1)

            if no_data_value is None:
                no_data_value = band.GetNoDataValue()

            if file_for_copy is None:
                file_for_copy = file_path

            week.append(band.ReadAsArray())

            del band
            del file

        if len(week) == 0:
            return
        try:
            week = np.ma.masked_values(np.stack(week), no_data_value, copy=False)
            week = np.ma.average(week, 0)
        except ValueError:
            del week
            print(
                '** ERROR ** Could not create: {0}'.format(
                    self.file_name(start_day)
                )
            )
            return

        dst_ds = self.GDAL_DRIVER.CreateCopy(
            self.file_name(start_day),
            gdal.Open(file_for_copy),
            strict=0,
            options=self.GDAL_OPTIONS
        )

        band = dst_ds.GetRasterBand(1)
        band.SetNoDataValue(no_data_value)
        gdalnumeric.BandWriteArray(band, week.filled(no_data_value))

        print(
            '  Saved output file to:\n  ' + str(self.file_name(start_day))
        )

        del band
        del dst_ds

    def create(self):
        if not os.path.exists(self.source_folder):
            print('Given source folder does not exist: ' + self.source_folder)
            sys.exit()

        for start_day in self.start_days_in_year():
            print('Processing day: {0} for year: {1}'.format(start_day,
                                                             self.year))

            self.create_for_day(start_day)

            print('\n')
