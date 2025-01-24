from django.db import models


# Create your models here.
class DiagnoseReport(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        NON_BINARY = "Non-binary"

    class OptionalBoolean(models.TextChoices):
        YES = "Yes"
        NO = "No"
        UNKNOWN = "Unknown"

    id = models.AutoField(primary_key=True)
    diagnose_result = models.BooleanField()
    confidence = models.FloatField()
    camera_type = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    diabetes_history = models.CharField(max_length=10, choices=OptionalBoolean.choices)
    family_diabetes_history = models.CharField(
        max_length=10, choices=OptionalBoolean.choices
    )
    weight = models.FloatField()
    height = models.FloatField()
    fundus_image = models.ImageField(upload_to="fundus_images/")
