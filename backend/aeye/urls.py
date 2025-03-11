from django.urls import path
from .views import DiagnoseAPIView, ImageQualityAPIView

urlpatterns = [
    path("diagnose/", DiagnoseAPIView.as_view(), name="diagnose"),
    path("image-quality/", ImageQualityAPIView.as_view(), name="image_quality"),
]
