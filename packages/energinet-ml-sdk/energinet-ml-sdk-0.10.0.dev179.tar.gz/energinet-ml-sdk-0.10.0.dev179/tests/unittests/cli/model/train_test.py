from unittest.mock import Mock, patch

from click.testing import CliRunner

from energinetml.cli.model.train import train
from energinetml.core.model import TrainedModel


class TestModelTrain:
    @patch("energinetml.cli.model.train.backend")
    def test__model_not_implemented__should_abort(self, backend_mock, model_path):
        """
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        context = Mock()
        context.train_model.side_effect = NotImplementedError
        context.get_tags.return_value = {}
        context.get_parameters.return_value = {}
        backend_mock.get_local_training_context.return_value = context

        # Act
        result = runner.invoke(cli=train, args=["--path", model_path])

        # Assert
        assert result.exit_code == 1
        assert isinstance(result.exception, NotImplementedError)

    @patch("energinetml.cli.model.train.backend")
    def test__model_returned_something_other_than_trained_model__should_abort(
        self, backend_mock, model_path
    ):
        """
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        context = Mock()
        trained_model = Mock()
        context.train_model.return_value = trained_model
        context.get_tags.return_value = {}
        context.get_parameters.return_value = {}
        backend_mock.get_local_training_context.return_value = context

        # Act
        result = runner.invoke(cli=train, args=["--path", model_path])

        # Assert
        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)

    @patch("energinetml.cli.model.train.backend")
    @patch("energinetml.cli.model.train.TrainedModel", new=Mock)
    def test__trained_model_does_not_verify__should_abort(
        self, backend_mock, model_path
    ):
        """
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        trained_model = Mock()
        trained_model.Invalid = TrainedModel.Invalid
        trained_model.verify.side_effect = TrainedModel.Invalid

        context = Mock()
        context.train_model.return_value = trained_model
        context.get_tags.return_value = {}
        context.get_parameters.return_value = {}
        backend_mock.get_local_training_context.return_value = context

        # Act
        result = runner.invoke(cli=train, args=["--path", model_path])

        # Assert
        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)

    @patch("energinetml.core.model.Model.dump")
    @patch("energinetml.cli.model.train.backend")
    @patch("energinetml.cli.model.train.TrainedModel", new=Mock)
    def test__should_dump_trained_model_correctly(
        self, backend_mock, model_dump_mock, model_path
    ):
        """
        :param Mock backend_mock:
        :param str model_path:
        """
        runner = CliRunner()

        trained_model = Mock()

        context = Mock()
        context.train_model.return_value = trained_model
        context.get_tags.return_value = {}
        context.get_parameters.return_value = {}
        backend_mock.get_local_training_context.return_value = context

        # Act
        result = runner.invoke(cli=train, args=["--path", model_path])

        # Assert
        assert result.exit_code == 0

        model_dump_mock.assert_called_once()
        context.save_artifacts.assert_called_once()
        context.save_meta_data.assert_called_once()
