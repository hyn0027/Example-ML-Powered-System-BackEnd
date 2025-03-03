import json, requests


def read_credentials():
    with open("credentials.json") as f:
        data = json.load(f)
    return int(data["USER_ID"]), data["API_KEY"]


USER_ID, API_KEY = read_credentials()


def post_metric(body):
    response = requests.post(
        "https://influx-prod-13-prod-us-east-0.grafana.net/api/v1/push/influx/write",
        headers={
            "Content-Type": "text/plain",
        },
        data=str(body),
        auth=(USER_ID, API_KEY),
    )

    status_code = response.status_code
    return status_code
