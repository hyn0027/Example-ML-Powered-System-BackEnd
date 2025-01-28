import requests
import json
from .models import DiagnoseReport


def read_credentials():
    with open("credentials.json") as f:
        data = json.load(f)
    return int(data["USER_ID"]), data["API_KEY"]


USER_ID, API_KEY = read_credentials()


def post_report(diagnose_report: DiagnoseReport, latency):
    body = (
        f"latency,"
        f"id={diagnose_report.id},"
        f"diagnose_result={diagnose_report.diagnose_result},"
        f"confidence={diagnose_report.confidence},"
        f"camera_type={diagnose_report.camera_type.replace(' ', '_')},"
        f"age={diagnose_report.age},"
        f"gender={diagnose_report.gender},"
        f"diabetes_history={diagnose_report.diabetes_history},"
        f"family_diabetes_history={diagnose_report.family_diabetes_history},"
        f"weight={diagnose_report.weight},"
        f"height={diagnose_report.height},"
        "source=ToySysServer "
        f"value={latency}"
    )
    post_metric(body)


def post_accuracy(diagnose_report: DiagnoseReport, accurate):
    body = (
        f"diagnose_accuracy,"
        f"id={diagnose_report.id},"
        f"diagnose_result={diagnose_report.diagnose_result},"
        f"confidence={diagnose_report.confidence},"
        f"camera_type={diagnose_report.camera_type.replace(' ', '_')},"
        f"age={diagnose_report.age},"
        f"gender={diagnose_report.gender},"
        f"diabetes_history={diagnose_report.diabetes_history},"
        f"family_diabetes_history={diagnose_report.family_diabetes_history},"
        f"weight={diagnose_report.weight},"
        f"height={diagnose_report.height},"
        "source=ToySysServer "
        f"value={int(accurate)}"
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
