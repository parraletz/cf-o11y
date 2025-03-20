# Instrumented FastAPI Application

This project demonstrates a FastAPI application instrumented with OpenTelemetry to export telemetry data like traces, metrics, and logs to a specified endpoint.

## Overview

The application consists of several endpoints, each serving a unique purpose and instrumented for observability. Below we provide a detailed explanation of the setup and individual components used in the application.

## Prerequisites

- Python 3.7+
- FastAPI
- OpenTelemetry Libraries
- An OpenTelemetry Collector (or compatible telemetry endpoint) running locally or configured as per your environment

## Code Summary

### Imports

```python
import logging
import random
import time

import uvicorn
from fastapi import FastAPI, Request
# OpenTelemetry imports
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
```

These are the necessary imports to define the FastAPI application, manage metrics, traces, logs, and utilize OpenTelemetry tools for detailed instrumentation.

### Resource Definition

```python
resource = Resource(attributes={
    SERVICE_NAME: "cf-o11y-instrumentor",
    SERVICE_VERSION: "1.0-BETA"
})
```

Defines the application’s resources, which include the service name and version for telemetry data attribution.

### Trace Provider Setup

```python
set_tracer_provider(TracerProvider(resource=resource))
get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
)
```

Sets up the TracerProvider with a BatchSpanProcessor that exports traces to the OpenTelemetry Collector endpoint specified by the URL.

### Metrics Provider Setup

```python
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics"))
metricsProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(metricsProvider)
```

Configures the MeterProvider, which handles metric data and periodically exports it to the specified metrics endpoint.

### Logger Setup

```python
logger_exporter = OTLPLogExporter(endpoint="http://localhost:4318/v1/logs")
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(logger_exporter))

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

set_logger_provider(logger_provider)
```

Initializes a LoggerProvider for log records, using a BatchLogRecordProcessor for exporting logs. It also adds a `LoggingHandler` to the root logger.

### FastAPI Application and Instrumentation

```python
instrumentor = FastAPIInstrumentor()
logger = logging.getLogger("CF-Service-auto")

app = FastAPI()

instrumentor.instrument_app(app, excluded_urls="/health", meter_provider=metricsProvider)
```

Creates the FastAPI application and initializes the `FastAPIInstrumentor` to automatically instrument the application, excluding the `/health` endpoint from auto-instrumentation metrics.

### Endpoints

#### Health Check

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

Provides a simple health check status.

#### Slow Endpoint

```python
@app.get("/slow")
def slow_endpoint():
    time.sleep(random.uniform(0.5, 2.0))
    return {"message": "This endpoint is slow"}
```

Simulates a slow response with a random delay between 0.5 to 2 seconds.

#### Error Simulation

```python
@app.get("/error")
def error_endpoint():
    raise ValueError("This is a simulated error")
```

Intended to raise an error, allowing you to test error handling and logging.

#### Compute Endpoint

```python
@app.get("/compute")
def compute_endpoint(n: int = 10):
    result = sum(i ** 2 for i in range(n))
    return {"result": result}
```

Performs a computation (sum of squares) and returns the result for a given integer `n`.

#### Server Request Echo

```python
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
```

Echoes back the request headers, query parameters, and body, useful for debugging client-server interactions.

### Running the Application

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

Launches the application using Uvicorn, with live reload enabled.

## Usage

To start the service, ensure your OpenTelemetry Collector is running and execute:

```bash
uvicorn instrumentation.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the Endpoints

Use a tool like `curl` or Postman, or a web browser to interact with the endpoints defined above.

### Configure Your Collector

Ensure your OpenTelemetry Collector configuration matches the endpoints specified for traces, metrics, and logs to capture telemetry data.

## Contribution

Feel free to fork and contribute improvements or bug fixes via pull requests.

## License

This project is licensed under the MIT License.