import os
import tempfile
from pathlib import Path

import pytest

from energinetml.core.files import FileMatcher


@pytest.fixture
def file_matcher():
    with tempfile.TemporaryDirectory() as path:
        yield FileMatcher(path=path)


class TestFileMatcher:
    def test__file_exists__should_return_correct_path(self):
        with tempfile.TemporaryDirectory() as path:
            Path(os.path.join(path, "f.json")).touch()
            Path(os.path.join(path, "f2.txt")).touch()
            os.makedirs(os.path.join(path, "subfolder"))
            Path(os.path.join(path, "subfolder", "f3.json")).touch()
            Path(os.path.join(path, "subfolder", "f4.txt")).touch()

            uut = FileMatcher(
                root_path=path,
                include=["**/*.json", "**/*.txt"],
                exclude=["subfolder/*.txt"],
            )

            matches = list(uut)

            assert len(matches) == 3
            assert "f.json" in matches
            assert "f2.txt" in matches
            assert os.path.join("subfolder", "f3.json") in matches
