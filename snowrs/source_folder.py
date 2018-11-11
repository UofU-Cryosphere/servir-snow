import fnmatch
import glob
import os
import shutil


class SourceFolder:
    SOURCE_FILE_TYPE = '*.tif'
    FOLDER_NAME_PATTERN = '20[0,1,2][0-9]*/'

    FOLDER_TYPES = {
        'forcing': 'forcing',
        'fraction': 'snow_fraction',
        '': ''
    }

    def __init__(self, base_path, **kwargs):
        self.type = kwargs.get('source_type', '')
        self.base_path = base_path
        self.year = None
        self.source_file_type = kwargs.get(
            'source_file_type', self.SOURCE_FILE_TYPE
        )

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value in SourceFolder.FOLDER_TYPES:
            self._type = value

    @property
    def source_file_type(self):
        return self._source_file_type

    @source_file_type.setter
    def source_file_type(self, value):
        self._source_file_type = value

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = os.path.join(value, '')

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        self._year = value

    @property
    def files(self):
        return glob.glob(self.type_path + self.source_file_type)

    @property
    def type_path(self):
        """
        Absolute path for set type and year.
        Example: /Path/To/Base/2000/forcing
        """
        return os.path.join(
            self.base_path, str(self.year), self.FOLDER_TYPES[self.type], ''
        )

    @staticmethod
    def doy_from_file_name(filename):
        return filename.split('.')[1][1:]

    @staticmethod
    def ensure_source_folder(folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    @staticmethod
    def check_duplicate(file, source_folder_for_file):
        duplicate = os.path.join(source_folder_for_file, os.path.basename(file))
        if os.path.exists(duplicate):
            os.remove(duplicate)

    def process_new_files(self):
        """
        Checks base_path for individual day files and moves them to their
        corresponding day folder
        """
        [self.__move_files_to_folder(file) for file in self.files]

    def __move_files_to_folder(self, file):
        """
        Moves given file to corresponding day folder

        :param file: Name of file to move
        """
        doy = self.doy_from_file_name(file)
        source_folder_for_file = os.path.join(self.type_path, doy)

        self.ensure_source_folder(source_folder_for_file)

        if fnmatch.fnmatch(file, '*' + doy + '*'):
            self.check_duplicate(file, source_folder_for_file)
            shutil.move(file, source_folder_for_file)

    def doy_folders(self):
        """
        Return a list of day folders in base path
        :return: Enumerable
        """
        return glob.glob(self.type_path + self.FOLDER_NAME_PATTERN)
