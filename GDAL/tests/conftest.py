import datetime
import gdal_merge
import os
import pytest
import shutil

from click.testing import CliRunner

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_TIFFS = os.path.join(TEST_ROOT, 'source_tiffs')
TEST_SOURCE_FOLDER = os.path.join(TEST_ROOT, 'source_folder')


def get_cls_marker(cls):
    return next(
        (mark for mark in cls.pytestmark if mark.name == 'runner_args')
    )


def create_source_folder(name):
    year = datetime.date.today().year
    test_source_folder = os.path.join(
        TEST_SOURCE_FOLDER, str(year), name, str(year) + '001'
    )
    if os.path.exists(test_source_folder):
        shutil.rmtree(test_source_folder)

    shutil.copytree(TEST_TIFFS, test_source_folder)


def execute_runner(source_type):
    arguments =  [
        '--source-folder', TEST_SOURCE_FOLDER,
        '--source-type', source_type
    ]

    cli_runner = CliRunner()
    return cli_runner.invoke(gdal_merge.process_folder, arguments)


@pytest.fixture(scope='class', autouse=True)
def runner(request):
    mark = get_cls_marker(request.cls)
    source_type = mark.kwargs['source_type']

    create_source_folder(source_type)

    request.cls.runner = execute_runner(source_type)

    yield

    shutil.rmtree(TEST_SOURCE_FOLDER)
