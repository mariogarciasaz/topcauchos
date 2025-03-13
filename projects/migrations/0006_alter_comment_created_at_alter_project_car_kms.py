# Generated by Django 5.0.1 on 2025-03-05 21:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_car_project_car_kms_alter_comment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 5, 22, 3, 1, 319143)),
        ),
        migrations.AlterField(
            model_name='project',
            name='car_kms',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
