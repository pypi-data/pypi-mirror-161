"""[summary]
"""
import sys
from datetime import datetime

import pytest

from energinetml.core.logger import ConsoleLogger, MetricsLogger
from energinetml.settings import DEFAULT_LOG_ENCODING


@pytest.fixture()
def clog(monkeypatch, tmp_path):
    monkeypatch.setattr("energinetml.core.logger.DEFAULT_LOG_PATH", tmp_path)
    yield ConsoleLogger(name="stdout", console=sys.stdout)


LOG_TEXT = "This messages come from the unit test.\n"
N_WRITES = 5


class TestConsoleLogger:
    """Unittests for the ConsoleLogger class."""

    def test__isatty(self, clog):
        """
        Test for requried class function.
        This function must return flase.
        """
        assert not clog.isatty()

    def test__flush(self, clog):
        """Test for requried class function."""
        clog.flush()

    def test__write(self, clog):
        """Test for requried class function."""

        # Act
        for _ in range(N_WRITES):
            clog.write(f"{datetime.now()} {LOG_TEXT}")

        clog.flush()

        # Assert
        with open(clog.filepath, "r", encoding=DEFAULT_LOG_ENCODING) as handle:
            lines = handle.readlines()

        assert len(lines) == N_WRITES
        for text in lines:
            assert text.endswith(LOG_TEXT)


@pytest.fixture
def logger():
    yield MetricsLogger()


class TestMetricsLogger:
    def test__echo(self, logger):
        """
        :param MetricsLogger logger:
        """
        with pytest.raises(NotImplementedError):
            logger.echo("s")

    def test__log(self, logger):
        """
        :param MetricsLogger logger:
        """
        with pytest.raises(NotImplementedError):
            logger.log("name", "value")

    def test__tag(self, logger):
        """
        :param MetricsLogger logger:
        """
        with pytest.raises(NotImplementedError):
            logger.tag("key", "value")

    def test__dataframe(self, logger):
        """
        :param MetricsLogger logger:
        """
        with pytest.raises(NotImplementedError):
            logger.dataframe("name", "df")
