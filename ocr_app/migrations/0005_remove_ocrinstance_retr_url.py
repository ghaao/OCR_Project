# Generated by Django 3.0.2 on 2020-01-20 02:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_app', '0004_ocrinstance_retr_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocrinstance',
            name='RETR_URL',
        ),
    ]
