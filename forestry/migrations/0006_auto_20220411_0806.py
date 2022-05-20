# Generated by Django 3.0.4 on 2022-04-11 06:06

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forestry', '0005_auto_20201011_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='description_rw',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='summary_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='summary_rw',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='text_en',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='text'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='text_rw',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='text'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='title_en',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='title_rw',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
    ]