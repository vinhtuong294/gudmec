# Generated by Django 4.2.16 on 2024-12-04 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datlich", "0003_patientrepository_userrepository_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="avatar",
            field=models.TextField(blank=None, null=True),
        ),
    ]
