import datetime
import os

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_TIFFS_DIR = os.path.join(TEST_ROOT, 'source_tiffs')
TEST_SOURCE_FOLDER = os.path.join(TEST_ROOT, 'source_folder')
RUN_YEAR = str(datetime.date.today().year)
DAY_OF_YEAR = '001'