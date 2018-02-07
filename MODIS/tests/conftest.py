import pytest
import shutil

from .constants import TEST_SOURCE_FOLDER
from .test_helper import create_source_folder, execute_runner, OutputFile


# Utility method to get a pytest marker from a test class
def get_cls_marker(cls, name):
    return next(
        (mark for mark in cls.pytestmark if mark.name == name)
    )


@pytest.fixture(scope='class', autouse=True)
def runner(request):
    mark = get_cls_marker(request.cls, 'runner_args')
    source_type = mark.kwargs['source_type']

    create_source_folder(source_type)

    request.cls.runner = execute_runner(source_type)
    request.cls.out_file = OutputFile(source_type)

    yield

    shutil.rmtree(TEST_SOURCE_FOLDER)
