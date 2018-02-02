import os
import fnmatch
import shutil
import glob


class SourceFolder:
    SOURCE_FILE_TYPES = '*.tif'
    FOLDER_NAME_PATTERN = '20[0,1,2][0-9]*/'

    def __init__(self, source_folder):
        self.source_folder = self.__ensure_slash(source_folder)
        self.files = glob.glob(self.source_folder + self.SOURCE_FILE_TYPES)
        self.new_days = sorted(self.__get_new_days())

    def __get_new_days(self):
        return {self.doy_from_file_name(filename) for filename in self.files}

    def get_folders_to_process(self):
        return glob.glob(self.source_folder + self.FOLDER_NAME_PATTERN)

    def scan_for_new_files(self):
        [
            self.__move_files_to_folder(file)
            for file in self.files
        ]

    def __move_files_to_folder(self, file):
        for doy in self.new_days:
            source_folder_for_file = \
                self.__ensure_slash(self.source_folder + doy)

            self.ensure_source_folder(source_folder_for_file)

            if fnmatch.fnmatch(file, '*' + doy + '*'):
                shutil.move(file, source_folder_for_file)
                return

    @staticmethod
    def doy_from_file_name(filename):
        return filename.split('.')[1][1:]

    @staticmethod
    def ensure_source_folder(folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    @staticmethod
    def __ensure_slash(value):
        if not value.endswith('/'):
            return value + '/'
        else:
            return value
