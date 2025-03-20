# FastAPI Application with OpenTelemetry Instrumentation

This project is a FastAPI application instrumented with OpenTelemetry to collect and export telemetry data, such as traces, metrics, and logs.

## Overview

The application consists of various endpoints, each instrumented to capture telemetry. The data is exported to an OpenTelemetry Collector configured to listen on localhost.

## Prerequisites

- Python 3.7+
- FastAPI
- OpenTelemetry Libraries
- An OpenTelemetry Collector running locally or accessible remotely

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/parraletz/cf-o11y.git
   cd cf-o11y
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn manual.main:app --host 0.0.0.0 --port 8001 --reload
   ```

## Code Explanation

### Logging and Imports

```python
import logging
import random
import time

import uvicorn
from fastapi import FastAPI, Request
```
- **`logging`**: Utilized for logging messages throughout the application.
- **`random`** and **`time`**: Used for simulating delays and measuring execution time.
- **`uvicorn`**: ASGI server to run FastAPI.
- **`FastAPI`, `Request`**: Core FastAPI framework imports for implementing endpoints.

### OpenTelemetry Setup

```python
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
```

- **Metrics, Traces, Logs**: Set up using OpenTelemetry to monitor application performance.

### Resource Configuration

```python
resource = Resource(attributes={
    SERVICE_NAME: "cf-o11y",
    SERVICE_VERSION: "1.0-BETA"
})
```
Defines application resource metadata, including service name and version for telemetry data attribution.

### Tracing

```python
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
trace.set_tracer_provider(provider)
trace.get_tracer_provider().add_span_processor(processor)
```
- Configures trace provider and exporter to send trace data to the specified OTLP endpoint.

### Metrics

```python
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
)
metricsProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(metricsProvider)
```
- Sets up a metrics provider with a periodic exporting metric reader to report metrics data.

### Logging

```python
logger_exporter = OTLPLogExporter(endpoint="http://localhost:4318/v1/logs")
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(logger_exporter))

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

logging.getLogger().addHandler(handler)

set_logger_provider(logger_provider)

logger = logging.getLogger("CF-Service")
```
- Configures the logging provider to export logs via OpenTelemetry's protocol.

### App Initialization

```python
app = FastAPI()
```
- Initializes the FastAPI application.

### Metrics Definition

```python
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

counters = {}
histograms = {}

def create_endpoint_metrics(endpoint_name):
    counters[endpoint_name] = meter.create_counter(
        name=f"{endpoint_name}_requests_total",
        description=f"Total number of requests to the {endpoint_name} endpoint",
        unit="1",
    )
    histograms[endpoint_name] = meter.create_histogram(
        name=f"{endpoint_name}_request_duration_seconds",
        description=f"Duration of {endpoint_name} endpoint requests",
        unit="s",
    )
```
- Defines functions to create custom metrics for monitoring request counts and durations for each endpoint.

### Endpoints

#### Health Check

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```
- Responds with a simple JSON to indicate service health.

#### Slow Endpoint

```python
@app.get("/slow")
def slow_endpoint():
    with tracer.start_as_current_span("slow_endpoint_span"):
        counters["slow"].add(1)
        start_time = time.time()

        time.sleep(random.uniform(0.5, 2.0))

        duration = time.time() - start_time
        histograms["slow"].record(duration)

        logger.info("slow endpoint")

        return {"message": "This endpoint is slow"}
```
- Simulates slow processing times and logs the request duration.

#### Error Simulation

```python
@app.get("/error")
def error_endpoint():
    with tracer.start_as_current_span("error_endpoint_span"):
        counters["error"].add(1)
        start_time = time.time()

        try:
            logger.error("error endpoint")
            raise ValueError("This is a simulated error")
        finally:
            duration = time.time() - start_time
            histograms["error"].record(duration)
            logger.error("error endpoint")
```
- Intentionally raises an error to demonstrate error tracking.

#### Computation

```python
@app.get("/compute")
def compute_endpoint(n: int = 10):
    with tracer.start_as_current_span("compute_endpoint_span") as span:
        counters["compute"].add(1)
        start_time = time.time()

        result = sum(i ** 2 for i in range(n))

        duration = time.time() - start_time
        histograms["compute"].record(duration)

        # Optionally, set attributes and events
        span.set_attribute("parameter.n", n)
        span.set_attribute("result", result)
        span.add_event("Completed computation")
        logger.info("result: " + str(result))
    return {"result": result}
```
- Performs a computational task on request and records the time taken.

#### Server Request Echo

```python
@app.get("/server_request")
async def server_request(request: Request):
    with tracer.start_as_current_span("server_request_span"):
        counters["server_request"].add(1)
        start_time = time.time()

        headers = dict(request.headers)
        query_params = dict(request.query_params)
        body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else {}

        duration = time.time() - start_time
        histograms["server_request"].record(duration)
        logger.info("The server requests has been processed successfully")
        return {
            "headers": headers,
            "query_params": query_params,
            "body": body
        }
```
- Echoes received request details back to the client for inspection.

### Running the Server

```python
if __name__ == "__main__":
    uvicorn.run("manual.main:app", host="0.0.0.0", port=8001, reload=True)
    logger.info("Starting the server on port 8001")
```
- Runs the application using Uvicorn with automatic reload enabled.

## Contributions

Contributions are welcome. Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.