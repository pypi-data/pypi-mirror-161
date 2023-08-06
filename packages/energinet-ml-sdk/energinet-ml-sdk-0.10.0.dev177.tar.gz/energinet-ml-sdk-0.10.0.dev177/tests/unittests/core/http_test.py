import typing
from enum import Enum
from unittest.mock import ANY, Mock, PropertyMock, patch

import pydantic
import pytest
from fastapi.testclient import TestClient

from energinetml.core.http import ModelMetaData, create_app, run_predict_api
from energinetml.settings import PACKAGE_REQUIREMENT

MODEL_NAME = "model-name"
MODEL_VERSION = "123"
MODEL_EXPERIMENT = "model-experiment"
MODEL_VALIDATOR = True
TEST_SERVER_BASE_URL = "https://testserver"
MODEL_DATASETS = ["dataset1", "dataset2"]
SUBSCRIPTION_ID = "subscription-id"
RESOURCE_GROUP = "resource-group"
WORKSPACE_NAME = "workspace-name"
RUN_ID = "run-id"
PORTAL_URL = "portal-url"
PORT = 5678
HOST = "host"

PREDICT_ENDPOINT = "/predict"
HEALTH_ENDPOINT = "/health"
METADATA_ENDPOINT = "/metadata"


# -- Request & Response models -----------------------------------------------


class IdentifierEnum(Enum):
    identifier1 = "identifier1"
    identifier2 = "identifier2"


class PredictFeatures(pydantic.BaseModel):
    feature1: int
    feature2: int


class PredictInput(pydantic.BaseModel):
    identifier: IdentifierEnum
    features: PredictFeatures


class PredictRequest(pydantic.BaseModel):
    inputs: typing.List[PredictInput]


class PredictResponse(pydantic.BaseModel):
    predictions: typing.List[typing.Any]


# -- Fixtures ----------------------------------------------------------------


def create_test_models():
    model = Mock()
    type(model).name = PropertyMock(return_value=MODEL_NAME)
    type(model).experiment = PropertyMock(return_value=MODEL_EXPERIMENT)
    type(model).datasets = PropertyMock(return_value=MODEL_DATASETS)

    trained_model = Mock()
    type(trained_model).validator = PropertyMock(return_value=MODEL_VALIDATOR)

    model_meta_data = ModelMetaData(
        model_version=MODEL_VERSION,
        model_name=model.name,
        model_experiment_id=model.experiment,
        has_validator=True if trained_model.validator else False,
        datasets=MODEL_DATASETS,
        subscription_id=SUBSCRIPTION_ID,
        resource_group=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME,
        run_id=RUN_ID,
        portal_url=PORTAL_URL,
    )

    meta_data = {
        "run_id": RUN_ID,
        "subscription_id": SUBSCRIPTION_ID,
        "resource_group": RESOURCE_GROUP,
        "workspace_name": WORKSPACE_NAME,
        "portal_url": PORTAL_URL,
    }

    return model, trained_model, model_meta_data, meta_data


@pytest.fixture
def controller():
    yield Mock(request_model=PredictRequest, response_model=PredictResponse)


@pytest.fixture
def client(controller):
    with patch(
        "energinetml.core.http.PredictionController"
    ) as PredictionController_mock:  # noqa: E501

        PredictionController_mock.return_value = controller

        model, trained_model, model_meta_data, _ = create_test_models()

        app = create_app(
            model=model,
            trained_model=trained_model,
            model_meta_data=model_meta_data,
            model_version=MODEL_VERSION,
        )

        yield TestClient(app)


@pytest.fixture
def client_with_opentelemetry(controller):
    with patch(
        "energinetml.core.http.PredictionController"
    ) as PredictionController_mock, patch(
        "energinetml.core.http.APPINSIGHTS_INSTRUMENTATIONKEY"
    ):

        PredictionController_mock.return_value = controller

        model, trained_model, model_meta_data, _ = create_test_models()

        app = create_app(
            model=model,
            trained_model=trained_model,
            model_version=MODEL_VERSION,
            model_meta_data=model_meta_data,
        )

        yield TestClient(app=app, base_url=TEST_SERVER_BASE_URL)


# -- health_http_endpoint() Tests --------------------------------------------


def test__health_http_endpoint__should_return_status_200(client):
    """
    :param TestClient client:
    """
    # Act
    response = client.get(HEALTH_ENDPOINT)

    # Assert
    assert response.status_code == 200


# -- metadata_http_endpoint() Tests --------------------------------------------


def test__metadata_http_endpoint__should_return_status_200_and_body(client):
    """
    :param TestClient client:
    """
    # Act
    response = client.get(METADATA_ENDPOINT)
    m = pydantic.parse_obj_as(ModelMetaData, response.json())

    # Assert
    assert response.status_code == 200

    assert m.model_version == MODEL_VERSION
    assert m.model_name == MODEL_NAME
    assert m.model_experiment_id == MODEL_EXPERIMENT
    assert m.datasets == MODEL_DATASETS
    assert m.has_validator == MODEL_VALIDATOR
    assert m.subscription_id == SUBSCRIPTION_ID
    assert m.resource_group == RESOURCE_GROUP
    assert m.workspace_name == WORKSPACE_NAME
    assert m.run_id == RUN_ID
    assert m.portal_url == PORTAL_URL


def test__metadata_http_endpoint__should_return_status_200(client):
    """
    :param TestClient client:
    """
    # Act
    response = client.get(METADATA_ENDPOINT)

    # Assert
    assert response.status_code == 200


# -- predict_http_endpoint() Tests -------------------------------------------


def test__predict_http_endpoint__omit_inputs__should_return_status_422(
    client, controller
):
    """
    :param TestClient client:
    :param Mock controller:
    """
    # Act
    response = client.post(PREDICT_ENDPOINT)

    # Assert
    assert response.status_code == 422
    controller.predict.assert_not_called()


def test__predict_http_endpoint__omit_identifier__should_return_status_422(
    client, controller
):
    """
    :param TestClient client:
    :param Mock controller:
    """
    # Act
    response = client.post(
        PREDICT_ENDPOINT,
        json={"inputs": [{"features": {"feature1": 1, "feature2": 2}}]},
    )

    # Assert
    assert response.status_code == 422
    controller.predict.assert_not_called()


def test__predict_http_endpoint__omit_feature__should_return_status_422(
    client, controller
):
    """
    :param TestClient client:
    :param Mock controller:
    """
    # Act
    response = client.post(
        PREDICT_ENDPOINT,
        json={
            "inputs": [
                {
                    "identifier": "identifier1",
                    "features": {
                        "feature1": 1,
                        # feature2 missing
                    },
                }
            ]
        },
    )

    # Assert
    assert response.status_code == 422
    controller.predict.assert_not_called()


def test__predict_http_endpoint__should_return_status_200(client, controller):
    """
    :param TestClient client:
    :param Mock controller:
    """
    controller.predict.return_value = PredictResponse(predictions=[1, 2])

    # Act
    response = client.post(
        PREDICT_ENDPOINT,
        json={
            "inputs": [
                {
                    "identifier": "identifier1",
                    "features": {"feature1": 1, "feature2": 2},
                }
            ]
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.headers["X-sdk-version"] == str(PACKAGE_REQUIREMENT)
    assert response.json() == {"predictions": [1, 2]}

    controller.predict.assert_called_once()


# -- OpenTelemetry middleware Tests ------------------------------------------


@patch("energinetml.core.http.tracer")
def test__opentelemetry_middleware__predict_raised_exception__should_log_exception(
    tracer_mock, client_with_opentelemetry, controller
):
    """
    :param Mock tracer_mock:
    :param TestClient client_with_opentelemetry:
    :param Mock controller:
    """
    controller.predict.side_effect = RuntimeError

    span = Mock()
    tracer_mock.start_span.return_value.__enter__.return_value = span

    # Act
    response = client_with_opentelemetry.post(
        PREDICT_ENDPOINT,
        json={
            "inputs": [
                {
                    "identifier": "identifier1",
                    "features": {"feature1": 1, "feature2": 2},
                }
            ]
        },
    )

    # Assert
    assert response.status_code == 500
    controller.predict.assert_called_once()

    # Common attributes
    span.set_attribute.assert_any_call("http.url", f"{TEST_SERVER_BASE_URL}/predict")
    span.set_attribute.assert_any_call("http_url", f"{TEST_SERVER_BASE_URL}/predict")
    span.set_attribute.assert_any_call("model_name", MODEL_NAME)
    span.set_attribute.assert_any_call("model_version", MODEL_VERSION)

    # Error attributes
    span.record_exception.assert_called_once()
    span.set_status.assert_called_once()
    span.set_attribute.assert_any_call("http.status_code", 500)
    span.set_attribute.assert_any_call("http_status_code", 500)
    span.set_attribute.assert_any_call("error.name", ANY)
    span.set_attribute.assert_any_call("error.message", ANY)
    span.set_attribute.assert_any_call("error.stacktrace", ANY)


@patch("energinetml.core.http.tracer")
def test__opentelemetry_middleware__predict_ok__should_log_status_code(
    tracer_mock, client_with_opentelemetry, controller
):
    """
    :param Mock tracer_mock:
    :param TestClient client_with_opentelemetry:
    :param Mock controller:
    """
    controller.predict.return_value = PredictResponse(predictions=[1, 2])

    span = Mock()
    tracer_mock.start_span.return_value.__enter__.return_value = span

    # Act
    response = client_with_opentelemetry.post(
        PREDICT_ENDPOINT,
        json={
            "inputs": [
                {
                    "identifier": "identifier1",
                    "features": {"feature1": 1, "feature2": 2},
                }
            ]
        },
    )

    # Assert
    assert response.status_code == 200
    controller.predict.assert_called_once()

    # Common attributes
    span.set_attribute.assert_any_call("http.url", f"{TEST_SERVER_BASE_URL}/predict")
    span.set_attribute.assert_any_call("http_url", f"{TEST_SERVER_BASE_URL}/predict")
    span.set_attribute.assert_any_call("model_name", MODEL_NAME)
    span.set_attribute.assert_any_call("model_version", MODEL_VERSION)

    # Success attributes
    span.set_status.assert_called_once()
    span.set_attribute.assert_any_call("http.status_code", 200)
    span.set_attribute.assert_any_call("http_status_code", 200)


# -- run_predict_api() Tests -------------------------------------------------


@patch("energinetml.core.http.create_app")
@patch("energinetml.core.http.uvicorn.run")
def test__run_predict_api__should_create_and_run_app(run_mock, create_app_mock):
    """
    :param Mock run_mock:
    :param Mock create_app_mock:
    """

    model, trained_model, model_meta_data, meta_data = create_test_models()

    app = Mock()

    create_app_mock.return_value = app

    # Act
    run_predict_api(
        model=model,
        trained_model=trained_model,
        meta_data=meta_data,
        model_version=MODEL_VERSION,
        host=HOST,
        port=PORT,
    )

    # Assert
    create_app_mock.assert_called_once_with(
        model=model,
        trained_model=trained_model,
        model_version=MODEL_VERSION,
        model_meta_data=model_meta_data,
    )

    run_mock.assert_called_once_with(app=app, host=HOST, port=PORT)
