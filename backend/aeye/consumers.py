from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import base64
import random
import time
from typing import Tuple, Optional
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from .models import DiagnoseReport
from .monitors import post_report

IMAGE_QUALITY_FAILED_RATE = 0.1
PROBABILITY_DIABETES = 0.4


class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "WebSocket connection established"}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        time_start = time.time()
        data = json.loads(text_data)

        form_data = data.get("formData")
        captured_photo = data.get("capturedPhoto")
        step_history = data.get("stepHistory")
        retake_count = data.get("retakeCount")

        print(f"Step history: {step_history}, Retake count: {retake_count}")

        # Validate form data
        valid_form, error_msg = await self.verify_form_data(form_data)
        if not valid_form:
            return await self.send(
                json.dumps(
                    {"message": "Invalid basic information", "errorMsg": error_msg}
                )
            )
        await self.send(json.dumps({"message": "Basic information verified"}))

        # Validate and decode image
        valid_image, image_data, error_msg = await self.verify_and_decode_image(
            captured_photo
        )
        if not valid_image:
            return await self.send(
                json.dumps({"message": "Invalid image data", "errorMsg": error_msg})
            )
        await self.send(json.dumps({"message": "Image data verified"}))

        # Perform diagnosis
        diagnose_result, confidence = await self.diagnose()
        await self.send(json.dumps({"message": "Diagnosis complete"}))

        # Generate and save report
        report, final_report = await self.generate_and_save_report(
            form_data, image_data, diagnose_result, confidence
        )
        await self.send(json.dumps({"message": "Report generated", "report": report}))

        # Log latency
        latency = time.time() - time_start
        post_report(final_report, latency)

    async def verify_form_data(self, form_data) -> Tuple[bool, Optional[str]]:
        await asyncio.sleep(random.random())
        if not form_data:
            return False, "No basic information provided"

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
        if camera_type == "Other" and not custom_camera_type:
            return False, "Custom camera type is required for 'Other'"

        valid_camera_types = {
            "Topcon NW400",
            "Canon CX-1",
            "Optos Daytona Plus",
            "Other",
        }
        if camera_type not in valid_camera_types:
            return False, "Invalid camera type"

        try:
            age, weight, height = (
                int(form_data["age"]),
                float(form_data["weight"]),
                float(form_data["height"]),
            )
        except ValueError:
            return False, "Age, weight, and height must be numbers"

        if not (0 <= age <= 160):
            return False, "Age must be between 0 and 160"
        if not (0 <= weight <= 500):
            return False, "Weight must be between 0 and 500"
        if not (0 <= height <= 300):
            return False, "Height must be between 0 and 300"

        valid_options = {"Yes", "No", "Unknown"}
        if (
            form_data["diabetesHistory"] not in valid_options
            or form_data["familyDiabetesHistory"] not in valid_options
        ):
            return False, "Invalid diabetes history values"
        if form_data["gender"] not in {"Female", "Male", "Non-binary"}:
            return False, "Invalid gender"

        return True, None

    async def verify_and_decode_image(
        self, image_data
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        await asyncio.sleep(random.random())
        if not image_data:
            return False, None, "No image data provided"

        decoded_image = await self.decode_base64_image(image_data)
        if not decoded_image:
            return False, None, "Failed to decode image data"

        if random.random() < IMAGE_QUALITY_FAILED_RATE:
            return False, decoded_image, "Image quality is too low"

        return True, decoded_image, None

    async def diagnose(self) -> Tuple[bool, float]:
        await asyncio.sleep(random.randint(2, 8))  # Simulate processing delay
        return random.random() < PROBABILITY_DIABETES, random.random()

    async def decode_base64_image(self, base64_image: str) -> Optional[bytes]:
        try:
            base64_data = base64_image.split("base64,")[-1]
            return base64.b64decode(base64_data)
        except Exception as e:
            print(f"Failed to decode image: {e}")
            return None

    async def generate_and_save_report(
        self, form_data, image_data, diagnose_result, confidence
    ):
        report_data = {"diagnose": diagnose_result, "confidence": confidence}
        report_id, final_report = await self.save_report(
            form_data, image_data, report_data
        )
        report_data["id"] = report_id
        return report_data, final_report

    async def save_report(self, form_data, image_data, report_data):
        report = await sync_to_async(DiagnoseReport.objects.create)(
            diagnose_result=report_data["diagnose"],
            confidence=report_data["confidence"],
            camera_type=(
                form_data["cameraType"]
                if form_data["cameraType"] != "Other"
                else form_data["customCameraType"]
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
