# Generated by Django 2.2.26 on 2022-01-11 08:58

from django.db import migrations, models
import quiz.models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_auto_20220106_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='figure',
            field=models.ImageField(blank=True, null=True, upload_to=quiz.models.figure_upload, verbose_name='Figure'),
        ),
    ]
