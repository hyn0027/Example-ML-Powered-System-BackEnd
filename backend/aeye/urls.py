from django.urls import path
from .views import DiagnoseAPIView

urlpatterns = [
    path("diagnose/", DiagnoseAPIView.as_view(), name="diagnose"),
]
