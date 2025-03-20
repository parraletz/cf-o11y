import logging
import random
import time

import uvicorn
from fastapi import FastAPI, Request
from opentelemetry import metrics
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_VERSION, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

resource = Resource(attributes={
    SERVICE_NAME: "cf-o11y-instrumentor",
    SERVICE_VERSION: "1.0-BETA"
})

set_tracer_provider(TracerProvider(resource=resource))
get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
)

reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics"))
metricsProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(metricsProvider)


logger_exporter = OTLPLogExporter(endpoint="http://localhost:4318/v1/logs")
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(logger_exporter))

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

set_logger_provider(logger_provider)
instrumentor = FastAPIInstrumentor()


logger = logging.getLogger("CF-Service-auto")

app = FastAPI()

instrumentor.instrument_app(app, excluded_urls="/health", meter_provider=metricsProvider)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/slow")
def slow_endpoint():
    time.sleep(random.uniform(0.5, 2.0))
    return {"message": "This endpoint is slow"}

@app.get("/error")
def error_endpoint():
    raise ValueError("This is a simulated error")

@app.get("/compute")
def compute_endpoint(n: int = 10):
    result = sum(i ** 2 for i in range(n))
    return {"result": result}

@app.get("/server_request")
async def server_request(request: Request):
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else {}
    return {
        "headers": headers,
        "query_params": query_params,
        "body": body
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
