# Generated by Django 5.0.1 on 2025-03-08 14:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_alter_comment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 8, 15, 50, 31, 714655)),
        ),
    ]
