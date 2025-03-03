import requests
import json
from .models import DiagnoseReport


def read_credentials():
    with open("credentials.json") as f:
        data = json.load(f)
    return int(data["USER_ID"]), data["API_KEY"]


USER_ID, API_KEY = read_credentials()


def post_report(diagnose_report: DiagnoseReport):
    body = (
        f"confidence,"
        f"id={diagnose_report.id},"
        f"diagnose_result={diagnose_report.diagnose_result},"
        f"camera_type={diagnose_report.camera_type.replace(' ', '_')},"
        f"age={diagnose_report.age},"
        f"age_group={diagnose_report.age // 10},"
        f"gender={diagnose_report.gender},"
        f"diabetes_history={diagnose_report.diabetes_history},"
        f"family_diabetes_history={diagnose_report.family_diabetes_history},"
        f"weight={diagnose_report.weight},"
        f"weight_group={diagnose_report.weight // 10},"
        f"height={diagnose_report.height},"
        f"height_group={diagnose_report.height // 10},"
        "source=ToySysServer "
        f"value={diagnose_report.confidence}"
    )
    post_metric(body)


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
