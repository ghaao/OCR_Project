# Generated by Django 3.0.2 on 2020-01-20 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_app', '0003_ocrinstance_chg_dttm'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocrinstance',
            name='RETR_URL',
            field=models.URLField(default='test.html', unique=True),
        ),
    ]