# Generated by Django 5.0.1 on 2025-03-04 19:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientdata', '0003_carhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carhistory',
            old_name='services',
            new_name='service',
        ),
    ]
