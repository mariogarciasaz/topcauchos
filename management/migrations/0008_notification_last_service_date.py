# Generated by Django 5.0.1 on 2025-03-08 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_alter_notification_notificated'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='last_service_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
