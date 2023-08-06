import os
import tempfile

import pytest

from energinetml.core.configurable import Configurable, locate_file_upwards

# This satisfies SonarCloud
SOME_FILE_NAME = "somefile.txt"


@pytest.fixture
def configurable():
    with tempfile.TemporaryDirectory() as path:
        yield Configurable(path=path)


# -- Tests -------------------------------------------------------------------


def test__locate_file_upwards__file_exists__should_return_correct_path():
    with tempfile.TemporaryDirectory() as path:
        starting_point = os.path.join(path, "some", "subfolder")
        target_file = os.path.join(path, SOME_FILE_NAME)

        os.makedirs(starting_point)

        with open(target_file, "w") as f:
            f.write("hello!")

        assert locate_file_upwards(starting_point, SOME_FILE_NAME) == target_file


def test__locate_file_upwards__file_does_not_exists__should_return_none():
    with tempfile.TemporaryDirectory() as path:
        starting_point = os.path.join(path, "some", "subfolder")

        os.makedirs(starting_point)

        assert locate_file_upwards(starting_point, SOME_FILE_NAME) is None
