from channels.generic.websocket import AsyncWebsocketConsumer
import json, asyncio, base64, random
from typing import Tuple, Optional, Dict, Any
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from .models import DiagnoseReport
from .utils import send_metric_to_grafana
from .config import IMAGE_QUALITY_FAILED_RATE, PROBABILITY_DIABETES


class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection establishment."""
        await self.accept()  # Accepts the WebSocket connection request
        await self.send_message("WebSocket connection established")

    async def receive(self, text_data: str):
        """Processes incoming WebSocket messages containing diagnosis requests."""
        data = json.loads(text_data)  # Parse received JSON data

        # Extract relevant data from the received message
        form_data = data.get("formData", {})  # Basic information about the user
        captured_photo = data.get("capturedPhoto", "")  # Base64-encoded image data
        step_history = data.get("stepHistory", [])  # History of users navigating different steps
        retake_count = data.get("retakeCount", 0)  # Number of times the user has retaken the photo

        # Step 1: Validate the received form data
        if not await self.verify_form_data(form_data):
            return
        await self.send_message("Basic information verified")

        # Step 2: Validate and decode the image
        image_data = await self.verify_and_decode_image(captured_photo)
        if image_data is None:
            # TODO: Send a metric to Grafana for failed image verification (implementation shown below)
            send_metric_to_grafana(
                metric_name="image_verification_failed",
                metric_value=1,
                labels={"camera_type": form_data.get("cameraType")},
            )

            return  # If image does not pass the test, stop further processing

        # TODO: Send a metric to Grafana for successful image verification with metric name "image_verification_pass"
        ...

        await self.send_message("Image data verified")

        # Step 3: Diagnose the disease
        diagnose_result, confidence = await self.diagnose(form_data, image_data)
        await self.send_message("Diagnosis complete")

        # Step 4: Generate and store the diagnosis report
        report = await self.generate_and_save_report(form_data, image_data, diagnose_result, confidence)
        await self.send_message("Report generated", {"diagnose": diagnose_result, "confidence": confidence, "id": report.id})

    async def send_message(self, message: str, data: Optional[Any] = None):
        """Helper function to send messages to the WebSocket client."""
        response = {"message": message}
        if data is not None:
            response["data"] = data  # Include additional data if provided
        await self.send(json.dumps(response))  # Send message as a JSON string

    async def verify_form_data(self, form_data: Dict[str, Any]) -> bool:
        """Validates the user-provided form data to ensure required fields are present."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulate processing delay

        # Define the required fields for validation
        required_fields = ["cameraType", "age", "gender", "diabetesHistory", "familyDiabetesHistory", "weight", "height"]
        missing_fields = [field for field in required_fields if not form_data.get(field)]

        if missing_fields:
            # Send error message if any required field is missing
            await self.send_message("Invalid basic information", f"Missing fields: {', '.join(missing_fields)}")
            return False

        return True  # Return True if validation passes

    async def verify_and_decode_image(self, image_data: str) -> Optional[bytes]:
        """Validates and decodes the base64-encoded image data."""
        await asyncio.sleep(random.uniform(0, 1))  # Simulate processing delay

        try:
            decoded_image = base64.b64decode(image_data.split("base64,")[-1])  # Decode the base64 image string
        except Exception as e:
            await self.send_message("Invalid image data", f"Error decoding image: {e}")  # Send an error message if decoding fails
            return None

        # Simulate random failure due to image quality issues
        if random.random() < IMAGE_QUALITY_FAILED_RATE:
            await self.send_message("Invalid image data", "Image quality is too low")
            return None

        return decoded_image  # Return decoded image data if valid

    async def diagnose(self, form_data, image_data) -> Tuple[bool, float]:
        """Simulates a diagnostic process and returns a result with confidence score."""
        await asyncio.sleep(random.randint(2, 8))  # Simulate AI processing delay

        # Generate a random diagnosis result and confidence level
        return random.random() < PROBABILITY_DIABETES, random.uniform(0.5, 1.0)

    async def generate_and_save_report(
        self,
        form_data: Dict[str, Any],
        image_data: bytes,
        diagnose_result: bool,
        confidence: float,
    ) -> DiagnoseReport:
        """Generates a diagnosis report and saves it to the database."""

        # Create a new report entry asynchronously
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

        # Save the captured fundus image with a unique filename
        image_file_name = f"fundus_image_{report.id}.jpg"
        image_file = await sync_to_async(ContentFile)(image_data, name=image_file_name)
        await sync_to_async(report.fundus_image.save)(image_file_name, image_file)

        # Ensure the report object is saved after updating the image field
        await sync_to_async(report.save)()

        return report  # Return the created report object
