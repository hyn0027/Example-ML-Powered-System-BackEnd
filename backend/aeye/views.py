from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from .config import PROBABILITY_DIABETES


class DiagnoseAPIView(APIView):
    def post(self, request, *args, **kwargs):
        form_data = request.data.get('formData')
        image_data = request.data.get('imageData')  # Expect base64 image

        # (Optional) Additional validation can be performed here

        # Simulate AI diagnostic process
        diagnose_result = random.random() < PROBABILITY_DIABETES
        confidence = round(random.uniform(0.5, 1.0), 2)

        return Response({
            "diagnose_result": diagnose_result,
            "confidence": confidence
        }, status=status.HTTP_200_OK)

class ImageQualityAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image_data = request.data.get('imageData')  # Expect base64 image

        # (Optional) Additional validation can be performed here

        # Simulate image quality check
        image_quality_passed = random.random() > 0.1

        return Response({
            "image_quality_passed": image_quality_passed
        }, status=status.HTTP_200_OK)