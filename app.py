from flask import Flask, request, jsonify, Response
from docker_logs import get_container_logs
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('flask_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_REQUESTS = Gauge('flask_active_requests', 'Active requests')
CONTAINER_LOG_REQUESTS = Counter('container_log_requests_total', 'Container log requests', ['container_id', 'status'])
CONTAINER_LOG_DURATION = Histogram('container_log_request_duration_seconds', 'Container log request duration')


@app.before_request
def before_request():
    ACTIVE_REQUESTS.inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    duration = time.time() - request.start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown'
    ).observe(duration)
    
    return response

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/fetch_logs', methods=['POST'])
def fetch_logs():
    """
    Fetch logs from a given container.
    Supports optional parameters for limiting logs.
    """
    
    start_time = time.time()
    data = request.json
    container_id = data.get("container")
    tail = data.get("tail")
    follow = data.get("follow", False)
    
    if not container_id:
        CONTAINER_LOG_REQUESTS.labels(container_id='unknown', status='error').inc()
        return jsonify({"error": "Container ID/Name required"}), 400
    
    try:
        logs = get_container_logs(container_id, tail=tail, follow=follow)

        if isinstance(logs, dict):  # If an error occurs
            CONTAINER_LOG_REQUESTS.labels(container_id=container_id, status='error').inc()
            return jsonify(logs), 500
        
        # Record successful request
        CONTAINER_LOG_REQUESTS.labels(container_id=container_id, status='success').inc()
        CONTAINER_LOG_DURATION.observe(time.time() - start_time)
        
        if follow:  # Streaming response for real-time logs
            return Response(logs, mimetype="text/plain")
        
        return jsonify({"logs": logs})
        
    except Exception as e:
        CONTAINER_LOG_REQUESTS.labels(container_id=container_id, status='error').inc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)