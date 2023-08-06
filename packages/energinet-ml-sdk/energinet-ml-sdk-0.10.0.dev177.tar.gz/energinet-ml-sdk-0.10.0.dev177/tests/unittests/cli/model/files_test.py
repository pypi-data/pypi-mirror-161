from unittest.mock import PropertyMock, patch

from click.testing import CliRunner

from energinetml.cli.model.files import files
from energinetml.core.model import Model
from tests.constants import FILES_INCLUDE

# -- create() Tests ----------------------------------------------------------


@patch("energinetml.cli.model.files.click.echo")
@patch.object(Model, "files", new_callable=PropertyMock)
def test__model_files__should_echo_model_files(model_files_mock, echo_mock, model):
    """
    :param Mock model_files_mock:
    :param Mock echo_mock:
    """
    runner = CliRunner()

    model_files_mock.return_value = FILES_INCLUDE

    # Act
    result = runner.invoke(cli=files, args=["--path", model.path])

    # Assert
    assert result.exit_code == 0
    assert echo_mock.call_count == len(FILES_INCLUDE)

    for file_name in FILES_INCLUDE:
        echo_mock.assert_any_call(file_name)
