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
        data = json.loads(text_data)

        form_data = data.get("formData", {})
        captured_photo = data.get("capturedPhoto", "")
        step_history = data.get("stepHistory", [])
        retake_count = data.get("retakeCount", 0)

        print(f"Form data: {form_data}\nCaptured photo: {captured_photo[:50]}...\nStep history: {step_history}\nRetake count: {retake_count}")

        # Validate form data
        if not await self.verify_form_data(form_data):
            return
        await self.send_message("Basic information verified")

        # Validate and decode image
        image_data = await self.verify_and_decode_image(captured_photo)
        if image_data is None:
            return
        await self.send_message("Image data verified")

        # Perform diagnosis
        diagnose_result, confidence = await self.diagnose(form_data, image_data)
        await self.send_message("Diagnosis complete")

        # Generate and save report
        report = await self.generate_and_save_report(form_data, image_data, diagnose_result, confidence)
        await self.send_message("Report generated", {"diagnose": diagnose_result, "confidence": confidence, "id": report.id})

        post_report(report)

    async def send_message(self, message: str, data: Optional[Any] = None):
        """Helper function to send messages over WebSocket."""
        response = {"message": message}
        if data is not None:
            response["data"] = data
        await self.send(json.dumps(response))

    async def verify_form_data(self, form_data: Dict[str, Any]) -> bool:
        """Validates user-provided form data."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulating async delay

        required_fields = ["cameraType", "age", "gender", "diabetesHistory", "familyDiabetesHistory", "weight", "height"]
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        if missing_fields:
            await self.send_message("Invalid basic information", f"Missing fields: {', '.join(missing_fields)}")
            return False

        return True

    async def verify_and_decode_image(self, image_data: str) -> Optional[bytes]:
        """Validates and decodes base64-encoded image data."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulating async delay

        try:
            decoded_image = base64.b64decode(image_data.split("base64,")[-1])
        except Exception as e:
            await self.send_message("Invalid image data", f"Error decoding image: {e}")
            return None

        if random.random() < IMAGE_QUALITY_FAILED_RATE:
            await self.send_message("Invalid image data", "Image quality is too low")
            return None

        return decoded_image

    async def diagnose(self, form_data, image_data) -> Tuple[bool, float]:
        """Simulates a diagnostic process."""
        await asyncio.sleep(random.randint(2, 8))  # Simulated processing delay
        return random.random() < PROBABILITY_DIABETES, random.uniform(0.5, 1.0)

    async def generate_and_save_report(
        self,
        form_data: Dict[str, Any],
        image_data: bytes,
        diagnose_result: bool,
        confidence: float,
    ) -> DiagnoseReport:
        """Generates and saves the diagnosis report."""
        report = await sync_to_async(DiagnoseReport.objects.create)(
            diagnose_result=diagnose_result,
            confidence=confidence,
            camera_type=(form_data["customCameraType"] if form_data["cameraType"] == "Other" else form_data["cameraType"]),
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
        return report
