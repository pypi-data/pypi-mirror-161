import requests


def test__deployment__health(deployment_base_url):
    """
    Invokes model health endpoint.

    :param str deployment_base_url:
    """

    # -- Act -----------------------------------------------------------------

    response = requests.get(url=f"{deployment_base_url}/health")

    # -- Assert --------------------------------------------------------------

    assert response.status_code == 200


def test__deployment__model_predict(
    deployment_base_url, prediction_input, prediction_output
):
    """
    Invokes prediction on a model using the provided base URL.

    :param str deployment_base_url:
    :param typing.Any prediction_input:
    :param typing.Any prediction_output:
    """

    # -- Act -----------------------------------------------------------------

    response = requests.post(
        url=f"{deployment_base_url}/predict", json=prediction_input
    )

    # -- Assert --------------------------------------------------------------

    assert response.status_code == 200
    assert response.json()["predictions"] == prediction_output
