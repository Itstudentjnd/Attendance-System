# Generated by Django 4.2.7 on 2024-05-11 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_recognition_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='encoding',
        ),
        migrations.AddField(
            model_name='student',
            name='mobile',
            field=models.CharField(default='', max_length=13),
        ),
    ]