import docker

client = docker.from_env()  # Connect to Docker daemon

def get_container_logs(container_id, tail=None, follow=False):
    """
    Fetch logs from a Docker container.
    
    :param container_id: Container name or ID.
    :param tail: Number of recent lines to fetch (default: all).
    :param follow: Whethzzer to stream logs in real-time.
    :return: Log output as a string or generator.


    example working api :
    curl -X POST http://localhost:5000/fetch_logs \
     -H "Content-Type: application/json" \
    -d '{"container": "container_id_or_name", "tail": 10, "follow": true}'

    """
    try:
        container = client.containers.get(container_id)

        if follow:  # Real-time streaming logs
            return container.logs(stream=True, tail=tail)

        logs = container.logs(tail=tail).decode("utf-8")
        return logs

    except docker.errors.NotFound:
        return {"error": f"Container '{container_id}' not found"}
    except Exception as e:
        return {"error": str(e)}
