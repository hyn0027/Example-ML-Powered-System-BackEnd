# Generated by Django 5.1.5 on 2025-01-24 20:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aeye', '0002_diagnosereport_fundus_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diagnosereport',
            old_name='diagnose_ID',
            new_name='id',
        ),
    ]
