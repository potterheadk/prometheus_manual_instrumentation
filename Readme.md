# Docker Log Fetcher with Prometheus Monitoring

This project provides a Flask-based API to fetch logs from Docker containers. It leverages the Docker SDK for Python (`docker`) to interact with the Docker daemon and retrieve container logs. Additionally, it integrates with Prometheus to expose metrics related to request handling and log fetching, allowing for monitoring and alerting on the application's performance.

## Features

- **Fetch Container Logs:** Retrieve logs from Docker containers by ID or name.
- **Tail Logs:** Specify the number of recent log lines to fetch using the `tail` parameter.
- **Real-time Log Streaming:** Stream logs in real-time using the `follow` parameter.
- **Prometheus Monitoring:** Expose metrics such as request count, request duration, active requests, and container log request statistics.
- **Error Handling:** Provides informative error responses for common issues like invalid container IDs or Docker API errors.

## Architecture

The project consists of the following components:

- **Flask API:** A Flask application that exposes the `/fetch_logs` endpoint for fetching logs and the `/metrics` endpoint for Prometheus metrics.
- **Docker SDK:** Uses the `docker` Python library to interact with the Docker daemon.
- **Prometheus Client:** Uses the `prometheus_client` library to create and expose metrics.
- **Docker Compose:** Defines the services (Flask app, Prometheus, Grafana) and their dependencies.

## Prerequisites

- **Docker:** Ensure Docker is installed and running on your system.
- **Docker Compose:** Ensure Docker Compose is installed.
- **Python 3.6+:** The application is written in Python 3.
- **pip:** Python package installer.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **prometheus.yml:** The `prometheus.yml` file configures Prometheus to scrape metrics from the Flask application. The provided configuration scrapes the `/metrics` endpoint on `localhost:5000`. You might need to adjust the `targets` setting if your Flask app runs on a different host or port.

2.  **docker-compose.yml:** The `docker-compose.yml` file defines the services for the application, Prometheus, and Grafana. You can customize the following:
    - `GF_SECURITY_ADMIN_PASSWORD`: The password for the Grafana admin user.
    - `GF_SERVER_HTTP_PORT`: The port Grafana will listen on. Make sure the port are not used by another service

## Usage

1.  **Start the application and monitoring stack:**

    ```bash
    docker-compose up --build
    ```

    This will build the Flask app image, start the Flask app, Prometheus, and Grafana containers.

2.  **Access the Flask API:**

    - **Fetch logs:**

      ```bash
      curl -X POST http://localhost:5000/fetch_logs \
           -H "Content-Type: application/json" \
           -d '{"container": "your_container_id_or_name", "tail": 10, "follow": false}'
      ```

      Replace `"your_container_id_or_name"` with the actual ID or name of the Docker container. Adjust `tail` and `follow` as needed. If `follow` is set to `true`, the response will be a stream of logs.

3.  **Access Prometheus:**

    - Open your web browser and navigate to `http://localhost:9090`. You can use the Prometheus UI to query and visualize the collected metrics.

4.  **Access Grafana:**

    - Open your web browser and navigate to `http://localhost:3001`.
    - Log in with username `admin` and the password you set in the `GF_SECURITY_ADMIN_PASSWORD` environment variable in `docker-compose.yml`.
    - Configure Prometheus as a data source in Grafana. The URL will typically be `http://prometheus:9090` (or `http://localhost:9090` if running outside of Docker Compose).
    - Create dashboards to visualize the metrics exposed by the Flask application. Example metrics:
      - `flask_requests_total`: Total number of requests.
      - `flask_request_duration_seconds_bucket`: Request duration histogram.
      - `flask_active_requests`: Number of active requests.
      - `container_log_requests_total`: Total number of container log requests.
      - `container_log_request_duration_seconds_bucket`: Container log request duration histogram.

## Code Explanation

### `app.py`

- **Imports:** Imports necessary libraries from Flask, the Docker log fetching module, and the Prometheus client.
- **Prometheus Metrics:** Defines Prometheus metrics to track request counts, duration, and other relevant data.
- **`before_request`:** A Flask decorator that executes before each request. It increments the `ACTIVE_REQUESTS` gauge and records the start time of the request.
- **`after_request`:** A Flask decorator that executes after each request. It decrements the `ACTIVE_REQUESTS` gauge, calculates the request duration, and updates the `REQUEST_COUNT` and `REQUEST_DURATION` metrics.
- **`/metrics` endpoint:** Exposes the Prometheus metrics in the required format.
- **`/fetch_logs` endpoint:** Handles requests to fetch container logs. It retrieves the container ID, tail, and follow parameters from the request body, calls the `get_container_logs` function, and returns the logs or an error message. It also updates the `CONTAINER_LOG_REQUESTS` and `CONTAINER_LOG_DURATION` metrics.
- **`if __name__ == '__main__':`:** Starts the Flask development server.

### `docker_logs.py`

- **`get_container_logs(container_id, tail=None, follow=False)`:** Fetches logs from a Docker container.
  - Takes the container ID, tail (number of lines), and follow (stream logs) parameters as input.
  - Uses the Docker SDK to connect to the Docker daemon.
  - Retrieves the container object using the container ID.
  - If `follow` is True, it streams the logs in real-time.
  - If `follow` is False, it retrieves the logs as a string.
  - Handles `docker.errors.NotFound` exceptions if the container is not found.
  - Handles other exceptions and returns an error message.

## Improvements and Considerations

- **Error Handling:** The project includes basic error handling, but it can be improved to handle more specific Docker API errors and provide more informative error messages.
- **Security:** For production environments, it's crucial to implement proper authentication and authorization mechanisms to protect the API.
- **Logging:** Add more comprehensive logging to the Flask application to track requests, errors, and other events. Consider using a logging library like `logging` module.
- **Configuration:** Use environment variables or a configuration file to manage application settings like the Docker API endpoint and Prometheus metrics port.
- **Input Validation:** Implement input validation to ensure that the container ID and other parameters are valid.
- **Asynchronous Tasks:** For long-running tasks like streaming logs, consider using asynchronous task queues (e.g., Celery) to avoid blocking the Flask application.
- **Container Healthchecks:** Define healthchecks for the Flask application in the `docker-compose.yml` file to ensure that it is running correctly.
- **Grafana Dashboards:** Create pre-built Grafana dashboards to visualize the metrics exposed by the application. This makes it easier to monitor the application's performance and identify potential issues.
- **Production Deployment:** Use a production-ready WSGI server (e.g., Gunicorn, uWSGI) to deploy the Flask application.

## License

[Specify the license for your project, e.g., MIT License]
