from unittest.mock import ANY, patch

from click.testing import CliRunner

from energinetml.cli.model.build import build

# -------------- Tests ----------------------------------------------------------


@patch("energinetml.cli.model.build.build_prediction_api_docker_image")
def test__build_model__should__build_docker_image(
    build_prediction_api_docker_image_mock, model_path
):
    """
    :param Mock build_prediction_api_docker_image_mock:
    """
    runner = CliRunner()

    # Act
    result = runner.invoke(
        cli=build,
        args=[
            "--artifact-path",
            model_path,
            "--tag",
            "docker:tag",
            "--model-version",
            "123",
        ],
    )

    # Assert
    assert result.exit_code == 0

    build_prediction_api_docker_image_mock.assert_called_once_with(
        artifact_path=ANY,  # Temporary directory
        model_version="123",
        tag="docker:tag",
    )
