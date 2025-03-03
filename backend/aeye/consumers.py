from channels.generic.websocket import AsyncWebsocketConsumer
import json, asyncio, base64, random, time
from typing import Tuple, Optional, Dict, Any
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from .models import DiagnoseReport
from .monitors import post_report
from .config import IMAGE_QUALITY_FAILED_RATE, PROBABILITY_DIABETES


class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        await self.accept()
        await self.send_message("WebSocket connection established")

    async def receive(self, text_data: str):
        """Processes incoming WebSocket messages."""
        time_start = time.time()
        data = json.loads(text_data)

        form_data = data.get("formData", {})
        captured_photo = data.get("capturedPhoto")
        step_history = data.get("stepHistory", [])
        retake_count = data.get("retakeCount", 0)

        print(
            f"Form data: {form_data}\nCaptured photo: {captured_photo}\nStep history: {step_history}\nRetake count: {retake_count}"
        )

        # Validate form data
        valid_form, error_msg = await self.verify_form_data(form_data)
        if not valid_form:
            return await self.send_message("Invalid basic information", error_msg)

        await self.send_message("Basic information verified")

        # Validate and decode image
        valid_image, image_data, error_msg = await self.verify_and_decode_image(
            captured_photo
        )
        if not valid_image:
            return await self.send_message("Invalid image data", error_msg)

        await self.send_message("Image data verified")

        # Perform diagnosis
        diagnose_result, confidence = await self.diagnose()
        await self.send_message("Diagnosis complete")

        # Generate and save report
        report, final_report = await self.generate_and_save_report(
            form_data, image_data, diagnose_result, confidence
        )
        await self.send_message("Report generated", report)

        # Log latency
        latency = time.time() - time_start
        post_report(final_report, latency)

    async def send_message(self, message: str, data: Optional[Any] = None):
        """Helper function to send messages over WebSocket."""
        response = {"message": message}
        if data is not None:
            response["data"] = data
        await self.send(json.dumps(response))

    async def verify_form_data(
        self, form_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validates user-provided form data."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulating async delay

        required_fields = [
            "cameraType",
            "age",
            "gender",
            "diabetesHistory",
            "familyDiabetesHistory",
            "weight",
            "height",
        ]
        missing_fields = [
            field for field in required_fields if not form_data.get(field)
        ]

        if missing_fields:
            return False, f"Missing fields: {', '.join(missing_fields)}"

        camera_type = form_data.get("cameraType")
        custom_camera_type = form_data.get("customCameraType")
        valid_camera_types = {
            "Topcon NW400",
            "Canon CX-1",
            "Optos Daytona Plus",
            "Other",
        }

        if camera_type not in valid_camera_types:
            return False, "Invalid camera type"

        if camera_type == "Other" and not custom_camera_type:
            return False, "Custom camera type is required for 'Other'"

        try:
            int(form_data["age"])
            float(form_data["weight"])
            float(form_data["height"])
        except ValueError:
            return False, "Age, weight, and height must be valid numbers"

        valid_options = {"Yes", "No", "Unknown"}
        if (
            form_data.get("diabetesHistory") not in valid_options
            or form_data.get("familyDiabetesHistory") not in valid_options
        ):
            return False, "Invalid diabetes history values"

        if form_data.get("gender") not in {"Female", "Male", "Non-binary"}:
            return False, "Invalid gender"

        return True, None

    async def verify_and_decode_image(
        self, image_data: Optional[str]
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Validates and decodes base64-encoded image data."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulating async delay

        if not image_data:
            return False, None, "No image data provided"

        try:
            decoded_image = base64.b64decode(image_data.split("base64,")[-1])
        except Exception as e:
            return False, None, f"Error decoding image: {e}"
        if random.random() < IMAGE_QUALITY_FAILED_RATE:
            return False, decoded_image, "Image quality is too low"

        return True, decoded_image, None

    async def diagnose(self) -> Tuple[bool, float]:
        """Simulates a diagnostic process."""
        await asyncio.sleep(random.randint(2, 8))  # Simulated processing delay
        return random.random() < PROBABILITY_DIABETES, random.uniform(0.5, 1.0)

    async def generate_and_save_report(
        self,
        form_data: Dict[str, Any],
        image_data: bytes,
        diagnose_result: bool,
        confidence: float,
    ):
        """Generates and saves the diagnosis report."""
        report_data = {"diagnose": diagnose_result, "confidence": confidence}
        report_id, final_report = await self.save_report(
            form_data, image_data, report_data
        )
        report_data["id"] = report_id
        return report_data, final_report

    async def save_report(
        self, form_data: Dict[str, Any], image_data: bytes, report_data: Dict[str, Any]
    ):
        """Saves the report to the database."""
        report = await sync_to_async(DiagnoseReport.objects.create)(
            diagnose_result=report_data["diagnose"],
            confidence=report_data["confidence"],
            camera_type=(
                form_data["customCameraType"]
                if form_data["cameraType"] == "Other"
                else form_data["cameraType"]
            ),
            age=int(form_data["age"]),
            gender=form_data["gender"],
            diabetes_history=form_data["diabetesHistory"],
            family_diabetes_history=form_data["familyDiabetesHistory"],
            weight=float(form_data["weight"]),
            height=float(form_data["height"]),
        )
        image_file_name = f"fundus_image_{report.id}.jpg"
        image_file = await sync_to_async(ContentFile)(image_data, name=image_file_name)
        await sync_to_async(report.fundus_image.save)(image_file_name, image_file)
        await sync_to_async(report.save)()
        return report.id, report
