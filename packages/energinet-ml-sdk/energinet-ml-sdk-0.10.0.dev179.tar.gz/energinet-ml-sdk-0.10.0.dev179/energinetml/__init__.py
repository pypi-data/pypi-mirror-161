#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Energinet ML python module
"""


import logging

logging.getLogger("opentelemetry.trace.status").setLevel(logging.ERROR)


from .settings import (  # noqa: E402
    APPINSIGHTS_INSTRUMENTATIONKEY,
    PACKAGE_NAME,
    PACKAGE_VERSION,
)

__name__ = PACKAGE_NAME
__version__ = PACKAGE_VERSION

# OpenTelemetry must be configured before importing any packages using it
if APPINSIGHTS_INSTRUMENTATIONKEY:

    import os

    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    from opentelemetry import trace
    from opentelemetry.sdk.resources import (
        SERVICE_INSTANCE_ID,
        SERVICE_NAME,
        SERVICE_NAMESPACE,
        Resource,
    )
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import ALWAYS_ON  # noqa: E402

    conn = f"InstrumentationKey={APPINSIGHTS_INSTRUMENTATIONKEY}"
    exporter = AzureMonitorTraceExporter(connection_string=conn)
    span_processor = BatchSpanProcessor(exporter)

    _not_set: str = "NOTUSED"

    # webappName-modelVersion
    APPINSIGHTS_SERVICE_NAME: str = os.getenv("APPINSIGHTS_SERVICE_NAME", _not_set)
    # projectName
    APPINSIGHTS_SERVICE_NAMESPACE: str = os.getenv(
        "APPINSIGHTS_SERVICE_NAMESPACE", _not_set
    )
    # webappName-modelName-modelVersion
    APPINSIGHTS_SERVICE_INSTANCE_ID: str = os.getenv(
        "APPINSIGHTS_SERVICE_INSTANCE_ID", _not_set
    )

    trace.set_tracer_provider(
        TracerProvider(
            sampler=ALWAYS_ON,
            resource=Resource.create(
                {
                    SERVICE_NAME: APPINSIGHTS_SERVICE_NAME,
                    SERVICE_NAMESPACE: APPINSIGHTS_SERVICE_NAMESPACE,
                    SERVICE_INSTANCE_ID: APPINSIGHTS_SERVICE_INSTANCE_ID,
                }
            ),
        )
    )

    provider = trace.get_tracer_provider()
    provider.add_span_processor(span_processor)


# Importing pandas must be done before importing modules using OpenTelemetry,
# otherwise an (apparent) bug in Pandas causes an exception in a second thread
import pandas  # noqa: E402

from .cli import main  # noqa: E402
from .core.insight import (  # noqa: E402
    query_predictions,
    query_predictions_as_dataframe,
)
from .core.logger import MetricsLogger  # noqa: E402
from .core.model import LoadedModel, Model, ModelArtifact, TrainedModel  # noqa: E402
from .core.predicting import PredictionInput  # noqa: E402
from .core.project import Project  # noqa: E402
from .core.training import requires_parameter  # noqa: E402
