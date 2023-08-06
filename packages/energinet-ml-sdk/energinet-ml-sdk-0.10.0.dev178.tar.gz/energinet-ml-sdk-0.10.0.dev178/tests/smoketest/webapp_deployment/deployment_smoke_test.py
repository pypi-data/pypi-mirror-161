import requests


def test__deployment__model_predict(deployment_base_url):
    """
    Invokes prediction on a default ASGI webapp using the provided URL.

    :param str deployment_base_url:
    """

    # -- Act -----------------------------------------------------------------

    response = requests.get(url=f"{deployment_base_url}")

    # -- Assert --------------------------------------------------------------

    assert response.status_code == 200
    assert response.json()["message"] == "Hello World"
