from django.db import models


# Model to store diagnose reports
class DiagnoseReport(models.Model):
    # Enum for gender choices
    class GenderChoices(models.TextChoices):
        MALE = "Male"  # Represents male gender
        FEMALE = "Female"  # Represents female gender
        NON_BINARY = "Non-binary"  # Represents non-binary gender

    # Enum for optional boolean choices (Yes, No, Unknown)
    class OptionalBoolean(models.TextChoices):
        YES = "Yes"  # Indicates positive confirmation
        NO = "No"  # Indicates negative confirmation
        UNKNOWN = "Unknown"  # Indicates uncertainty

    # Primary key for the model, auto-incrementing
    id = models.AutoField(primary_key=True)

    # Stores the diagnosis result (True/False)
    diagnose_result = models.BooleanField()

    # Confidence level of the diagnosis (float value)
    confidence = models.FloatField()

    # Type of camera used for fundus imaging
    camera_type = models.CharField(max_length=100)

    # Patient's age
    age = models.IntegerField()

    # Patient's gender, must be one of the predefined choices
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)

    # Indicates if the patient has a history of diabetes
    diabetes_history = models.CharField(max_length=10, choices=OptionalBoolean.choices)

    # Indicates if the patient has a family history of diabetes
    family_diabetes_history = models.CharField(max_length=10, choices=OptionalBoolean.choices)

    # Patient's weight in kilograms
    weight = models.FloatField()

    # Patient's height in meters
    height = models.FloatField()

    # Fundus image of the patient's eye, stored in the "uploads/" directory
    fundus_image = models.ImageField(upload_to="uploads/")
