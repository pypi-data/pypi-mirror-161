#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import logging
import time
import traceback
from contextvars import ContextVar
from typing import TYPE_CHECKING, Callable, List, Optional  # noqa TYP001
from uuid import uuid4

import fastapi
import uvicorn
from opentelemetry import trace
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from energinetml.core.predicting import PredictionController, PredictResponse
from energinetml.settings import APPINSIGHTS_INSTRUMENTATIONKEY, PACKAGE_REQUIREMENT

if TYPE_CHECKING:
    from energinetml.core.model import Model, TrainedModel

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class ModelMetaData(BaseModel):
    """A meta data model container which holds information about the deployed model."""

    model_version: str
    model_name: str
    model_experiment_id: str
    datasets: List[str]
    has_validator: bool
    subscription_id: Optional[str] = None
    resource_group: Optional[str] = None
    workspace_name: Optional[str] = None
    run_id: Optional[str] = None
    portal_url: Optional[str] = None


def create_app(
    model: "Model",
    trained_model: "TrainedModel",
    model_meta_data: ModelMetaData,
    model_version: str = None,
) -> fastapi.FastAPI:
    """A function which defines the FastAPI structure.

    Args:
        model (Model): A Model object which is used and enriched during model training
        with our SDK.
        trained_model (TrainedModel): A TrainedModel object which is generated during
        model training with our SDK.
        model_meta_data (ModelMetaData, optional): A metadata container which is
        exposed on /metadata and can be used for model tracing..
        model_version (str, optional): A model identifer which is genereated during
        registration of an model. Defaults to None.

    Returns:
        fastapi.FastAPI: The structure of the webserver.
    """
    controller = PredictionController(
        model=model, trained_model=trained_model, model_version=model_version
    )

    async def opentelemetry_middleware(
        request: fastapi.Request, call_next: Callable
    ) -> fastapi.Response:
        """
        FastAPI middleware to record HTTP requests.

        Can not access request body in middleware (for logging):
        Issue description: https://github.com/tiangolo/fastapi/issues/394
        """
        start = time.perf_counter()
        correlation_id.set(str(uuid4()))

        # TODO: Why imports here?
        from opentelemetry.trace import SpanKind, Status
        from opentelemetry.trace.status import StatusCode

        start_span = tracer.start_span(name="request", kind=SpanKind.SERVER)

        with start_span as span:
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http_url", str(request.url))
            span.set_attribute("model_name", model.name)
            span.set_attribute("correlation_id", correlation_id.get())
            if model_version is not None:
                span.set_attribute("model_version", model_version)

            try:
                response = await call_next(request)
            except Exception as e:
                logger.exception("Prediction failed")
                span.record_exception(e)
                span.set_status(Status(status_code=StatusCode.ERROR))
                span.set_attribute("http.status_code", 500)
                span.set_attribute("http_status_code", 500)
                span.set_attribute("error.name", e.__class__.__name__)
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.stacktrace", traceback.format_exc())
                return fastapi.Response(status_code=500)
            else:
                span.set_status(Status(status_code=StatusCode.OK))
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http_status_code", response.status_code)
                end = time.perf_counter()
                span.set_attribute("duration_endpoint", str(end - start))
                return response

    async def root_http_endpoint() -> RedirectResponse:
        """
        / should redirect to /docs
        """
        return RedirectResponse(url="/docs")

    async def predict_http_endpoint(
        request: controller.request_model, response: fastapi.Response
    ) -> PredictResponse:
        """
        Model prediction HTTP endpoint.
        """
        response.headers["X-sdk-version"] = str(PACKAGE_REQUIREMENT)

        return controller.predict(request, correlation_id=correlation_id.get())

    async def health_http_endpoint(response: fastapi.Response) -> fastapi.Response:
        """
        Health endpoint, should return status 200 with no specific body.
        """
        response.status_code = 200
        return response

    async def metadata_http_endpoint(response: fastapi.Response) -> ModelMetaData:
        """
        Metadata endpoint, should return status 200 with a ModelMetaData body.
        """
        return model_meta_data

    # -- Setup app -----------------------------------------------------------

    if model_meta_data.portal_url:
        description = (
            "This model was trained via AzureML. The run can be found "
            f"<a href='{model_meta_data.portal_url}' target='_blank'>here</a>."
            f"\n\nModel version: {model_version}"
        )
    else:
        description = f"Model version: {model_version if model_version else None}"

    app = fastapi.FastAPI(
        title=model.name,
        description=description,
    )

    if APPINSIGHTS_INSTRUMENTATIONKEY:
        app.add_middleware(
            middleware_class=BaseHTTPMiddleware, dispatch=opentelemetry_middleware
        )

    app.router.add_api_route(path="/", methods=["GET"], endpoint=root_http_endpoint)

    app.router.add_api_route(
        path="/predict",
        methods=["POST"],
        endpoint=predict_http_endpoint,
        response_model=controller.response_model,
        tags=["model"],
        summary="Predict using the model",
    )

    app.router.add_api_route(
        path="/health",
        methods=["GET"],
        endpoint=health_http_endpoint,
        tags=["health"],
        summary="Health endpoint",
        description="Health endpoint, returns status 200",
    )

    app.router.add_api_route(
        path="/metadata",
        methods=["GET"],
        endpoint=metadata_http_endpoint,
        tags=["Metadata"],
        summary="Metadata endpoint",
        description="Metadata endpoint, returns status 200 with a ModelMetaData body",
    )

    return app


def run_predict_api(
    model: "Model",
    trained_model: "TrainedModel",
    meta_data,
    host: str,
    port: int,
    model_version: str = None,
) -> None:
    """Wrapper function used to enrich the defined endpoints.

    Args:
        model (Model): A Model object which is used and enriched during model training
        with our SDK.
        trained_model (TrainedModel): A TrainedModel object which is generated during
        model training with our SDK.
        host (str): Name of the host. This value is "127.0.0.1" when running local.
        port (int): Port number where the webserver is exposing defined endpoints to.
        model_version (str, optional): A model identifer which is genereated during
        registration of an model. Defaults to None.
    """

    model_meta_data = ModelMetaData(
        model_version=model_version,
        model_name=model.name,
        model_experiment_id=model.experiment,
        has_validator=True if trained_model.validator else False,
        datasets=model.datasets,
        subscription_id=meta_data["subscription_id"],
        resource_group=meta_data["resource_group"],
        workspace_name=meta_data["workspace_name"],
        run_id=meta_data["run_id"],
        portal_url=meta_data["portal_url"],
    )

    app = create_app(
        model=model,
        trained_model=trained_model,
        model_version=model_version,
        model_meta_data=model_meta_data,
    )

    uvicorn.run(app=app, host=host, port=port)
