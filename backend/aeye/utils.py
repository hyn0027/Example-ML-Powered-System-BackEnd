import json, requests
from typing import Dict


def read_credentials():
    """Reads user credentials from a JSON file and returns the user ID and API key."""
    with open("credentials.json") as f:
        data = json.load(f)
    return int(data["USER_ID"]), data["API_KEY"]


# Load user credentials from the file
USER_ID, API_KEY = read_credentials()


def send_metric_to_grafana(metric_name: str, metric_value, labels: Dict):
    """
    Formats and sends a metric to Grafana's InfluxDB endpoint.

    Args:
        metric_name (str): Name of the metric to send.
        metric_value (any): Value of the metric.
        labels (Dict): A dictionary of labels to associate with the metric.

    Returns:
        int: HTTP status code of the request.
    """
    # Construct the body of the metric in InfluxDB line protocol format
    body = (
        f"{metric_name},"
        + ",".join([f"{key}={value}" for key, value in labels.items()])
        + ",source=ToySysServer "
        + f"value={metric_value}"
    )

    # Send the metric and get the response status code
    status_code = post_metric(body)

    # Print the response status code
    print(f"Posted metric with status code: {status_code}")

    return status_code


def post_metric(body):
    """Sends a POST request to Grafana's InfluxDB endpoint with the given metric data."""
    response = requests.post(
        "https://influx-prod-13-prod-us-east-0.grafana.net/api/v1/push/influx/write",
        headers={
            "Content-Type": "text/plain",
        },
        data=str(body),
        auth=(USER_ID, API_KEY),
    )

    # Get the response status code
    status_code = response.status_code

    return status_code
