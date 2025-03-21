# FastAPI Application with OpenTelemetry Instrumentation

This repository hosts a FastAPI application instrumented with OpenTelemetry for enhanced observability. The application includes several endpoints, each providing unique functionality while collecting traces, metrics, and logs.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Telemetry](#telemetry)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

Follow the instructions below to clone the repository, set up your environment, and start using the application.

### Prerequisites

Ensure you have the following installed:

- Python 3.7+
- Uvicorn
- OpenTelemetry Libraries
- A running OpenTelemetry Collector or compatible telemetry endpoint

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/parraletz/cf-o11y.git
   cd cf-o11y
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate # on Windows use `venv\Scripts\activate`
   ```

3. **Install the Necessary Packages**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Interact with the application using a REST client like `curl`, Postman, or a web browser. The available endpoints include:

- **`/health`**: Check the health status of the service.
- **`/slow`**: Simulate a delayed response.
- **`/error`**: Trigger a simulated error.
- **`/compute`**: Perform a computational task.
- **`/server_request`**: Echo back request details.

### Telemetry

The application is configured to export telemetry data:

- **Traces**: Collected and exported to `http://localhost:4318/v1/traces`.
- **Metrics**: Periodically exported to `http://localhost:4318/v1/metrics`.
- **Logs**: Exported to `http://localhost:4318/v1/logs`.

Ensure your OpenTelemetry Collector is running and listening at these endpoints.

### Configuration

To modify the telemetry endpoint configurations, edit the `main.py` file:

```python
OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
OTLPLogExporter(endpoint="http://localhost:4318/v1/logs")
```

### Testing

It repo includes a locustfile for load testing the application.

```bash
locust -f tests/locustfile.py -u 100 -r 2 --run-time 20m --host=http://localhost:8001
```


### Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/YourFeature`).
6. Open a Pull Request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
