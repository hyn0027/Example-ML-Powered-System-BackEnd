from .models import DiagnoseReport
from .utils import post_metric


def post_report(diagnose_report: DiagnoseReport):
    body = (
        f"confidence,"
        f"diagnose_result={diagnose_report.diagnose_result},"
        f"camera_type={diagnose_report.camera_type.replace(' ', '_')},"
        "source=ToySysServer "
        f"value={diagnose_report.confidence}"
    )
    post_metric(body)
