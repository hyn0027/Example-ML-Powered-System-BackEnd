from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import base64
import random

from typing import Tuple, Optional

IMAGE_QUALITY_FAILED_RATE = 0.1

PROBABILITY_DIABETES = 0.4


class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "WebSocket connection established"}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        formData = data.get("formData")
        capturedPhoto = data.get("capturedPhoto")

        valid_form_data, form_data_error = await self.verify_form_data(formData)
        if not valid_form_data:
            await self.send(
                json.dumps(
                    {
                        "message": "Invalid basic information",
                        "errorMsg": form_data_error,
                    }
                )
            )
            return
        else:
            await self.send(json.dumps({"message": "Basic information verified"}))

        valid_image, image_data, image_data_error = await self.verify_and_decode_image(
            capturedPhoto
        )
        if not valid_image:
            await self.send(
                json.dumps(
                    {"message": "Invalid image data", "errorMsg": image_data_error}
                )
            )
            return
        else:
            await self.send(json.dumps({"message": "Image data verified"}))

        diagnose_result, confidence = await self.diagnose(formData, image_data)
        await self.send(json.dumps({"message": "Diagnosis complete"}))

        report = await self.generate_report(diagnose_result, confidence)
        await self.send(json.dumps({"message": "Report generated", "report": report}))

    async def verify_form_data(self, form_data) -> Tuple[bool, Optional[str]]:
        await asyncio.sleep(1)
        if not form_data:
            return False, "No basic information provided"
        camera_type = form_data.get("cameraType")
        custom_camera_type = form_data.get("customCameraType")
        age = form_data.get("age")
        gender = form_data.get("gender")
        diabetes_history = form_data.get("diabetesHistory")
        family_diabetes_history = form_data.get("familyDiabetesHistory")
        weight = form_data.get("weight")
        height = form_data.get("height")

        keys = [
            "cameraType",
            "age",
            "gender",
            "diabetesHistory",
            "familyDiabetesHistory",
            "weight",
            "height",
        ]
        missing_fields = [key for key in keys if not form_data.get(key)]
        if missing_fields:
            return False, f"Missing fields: {', '.join(missing_fields)}"
        if camera_type == "Other" and not custom_camera_type:
            return False, "Custom camera type is required for 'Other' camera type"
        if camera_type not in [
            "Topcon NW400",
            "Canon CX-1",
            "Optos Daytona Plus",
            "Other",
        ]:
            return False, "Invalid camera type"
        try:
            age = int(age)
            weight = float(weight)
            height = float(height)
        except ValueError:
            return False, "Invalid age, weight, or height, must be a number"
        if age < 0 or age > 160:
            return False, "Invalid age, must be between 0 and 160"
        if gender not in ["Female", "Male", "Other"]:
            return False, "Invalid gender, must be Female, Male, or Other"
        if diabetes_history not in ["Yes", "No", "Unknown"]:
            return False, "Invalid diabetes history, must be Yes, No, or Unknown"
        if family_diabetes_history not in ["Yes", "No", "Unknown"]:
            return False, "Invalid family diabetes history, must be Yes, No, or Unknown"
        if weight < 0 or weight > 500:
            return False, "Invalid weight, must be between 0 and 500"
        if height < 0 or height > 300:
            return False, "Invalid height, must be between 0 and 300"
        return True, None

    async def verify_and_decode_image(
        self, image_data
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        await asyncio.sleep(1)
        if not image_data:
            return False, None, "No image data provided"
        image_data = await self.decode_base64_image(image_data)
        if not image_data:
            return False, None, "Failed to decode image data"
        if random.random() < IMAGE_QUALITY_FAILED_RATE:
            return False, image_data, "Image quality low"
        return True, image_data, None

    async def diagnose(self, form_data, image_data) -> Tuple[bool, float]:
        """
        Diagnoses the patient based on the provided form data and image data.
        """
        # Simulate a long-running diagnosis process
        sleep_time = random.randint(5, 10)
        await asyncio.sleep(sleep_time)

        diagnose_result = random.random() < PROBABILITY_DIABETES
        confidence = random.random()
        return diagnose_result, confidence

    async def decode_base64_image(self, base64_image):
        """
        Decodes a base64 string into binary image data.
        """
        # Base64 string format: "data:image/<type>;base64,<encoded_data>"
        if "base64," in base64_image:
            header, base64_data = base64_image.split("base64,", 1)
        else:
            base64_data = base64_image

        # Decode the base64 string
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            print(f"Failed to decode base64 image: {e}")
            return None

    async def generate_report(self, diagnose_result, confidence):
        """
        Generates a report based on the diagnosis result and confidence.
        """
        report = {
            "diagnose": diagnose_result,
            "confidence": confidence,
        }
        return report
