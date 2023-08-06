from unittest.mock import ANY, MagicMock, Mock, PropertyMock, patch

from click.testing import CliRunner
from packaging.version import Version

from energinetml import PACKAGE_NAME
from energinetml.cli.model.submit import submit
from energinetml.core.model import Model


class TestModelSubmit:
    def test__download_and_not_wait__should_abort(self, model_path):
        """
        :param str model_path:
        """
        runner = CliRunner()

        # Act
        result = runner.invoke(
            cli=submit, args=["--path", model_path, "--download", "--nowait"]
        )

        # Assert
        assert result.exit_code == 1
        assert result.output.startswith(
            "Can not use -d/--download together with --nowait"
        )

    @patch.object(Model, "requirements", new_callable=PropertyMock)
    def test__package_name_not_in_requirements__should_abort(
        self, model_requirements_mock, model_path
    ):
        """
        :param Mock model_requirements_mock:
        :param str model_path:
        """
        runner = CliRunner()

        model_requirements_mock.return_value = []

        # Act
        result = runner.invoke(cli=submit, args=["--path", model_path])

        # Assert
        assert result.exit_code == 1
        assert result.output.startswith(
            f"Could not find '{PACKAGE_NAME}' in the project's requirements.txt file"
        )

    @patch("energinetml.cli.model.submit.backend")
    @patch.object(Model, "requirements", new_callable=MagicMock)
    def test__required_sdk_version_less_than_current__should_echo_warning(
        self, model_requirements_mock, backend_mock, model_path
    ):
        """
        :param Mock model_requirements_mock:
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        model_requirements_mock.__contains__.return_value = True
        model_requirements_mock.get_version.return_value = Version("0.0.0")

        # Act
        result = runner.invoke(cli=submit, args=["--path", model_path])

        # Assert
        assert result.exit_code == 0
        assert (
            (
                "WARNING: Your requirements.txt file contains a version of "
                "%s (0.0.0) which is older than your current installation"
            )
            % PACKAGE_NAME
        ) in result.output

    @patch("energinetml.cli.model.submit.backend")
    @patch.object(Model, "requirements", new_callable=MagicMock)
    def test__required_sdk_version_greater_than_current__should_echo_warning(
        self, model_requirements_mock, backend_mock, model_path
    ):
        """
        :param Mock model_requirements_mock:
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        model_requirements_mock.__contains__.return_value = True
        model_requirements_mock.get_version.return_value = Version("9999.9999.9999")

        # Act
        result = runner.invoke(cli=submit, args=["--path", model_path])

        # Assert
        assert result.exit_code == 0
        assert (
            (
                "WARNING: Your requirements.txt file contains a version of "
                "%s (9999.9999.9999) which is newer than your current installation "
            )
            % PACKAGE_NAME
        ) in result.output

    @patch("energinetml.cli.model.submit.backend")
    @patch.object(Model, "requirements", new_callable=MagicMock)
    def test__should_submit_wait_and_download_files(
        self, model_requirements_mock, backend_mock, model_path
    ):
        """
        :param Mock model_requirements_mock:
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        model_requirements_mock.__contains__.return_value = True
        model_requirements_mock.get_version.return_value = Version("9999.9999.9999")

        context = Mock()

        backend_mock.submit_model.return_value = context

        # Act
        result = runner.invoke(
            cli=submit,
            args=[
                "--path",
                model_path,
                "--wait",
                "--download",
                "parameter1",
                "parameter2",
            ],
        )

        # Assert
        assert result.exit_code == 0

        backend_mock.submit_model.assert_called_once_with(
            model=ANY, params=("parameter1", "parameter2")
        )

        context.wait_for_completion.assert_called_once()
        context.wait_for_completion.download_files()
