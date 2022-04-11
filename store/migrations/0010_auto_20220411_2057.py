# Generated by Django 3.0.4 on 2022-04-11 18:57

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20200816_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='seedpretreatment',
            name='process_en',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='seedpretreatment',
            name='process_rw',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='seedpretreatment',
            name='title_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='seedpretreatment',
            name='title_rw',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='seedproduct',
            name='short_note_en',
            field=models.TextField(blank=True, null=True, verbose_name='Short description'),
        ),
        migrations.AddField(
            model_name='seedproduct',
            name='short_note_rw',
            field=models.TextField(blank=True, null=True, verbose_name='Short description'),
        ),
        migrations.AddField(
            model_name='typesofseed',
            name='overview_en',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='overview'),
        ),
        migrations.AddField(
            model_name='typesofseed',
            name='overview_rw',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='overview'),
        ),
        migrations.AddField(
            model_name='typesofseed',
            name='storage_type_en',
            field=models.CharField(choices=[('RT', 'Room temperature'), ('CRT', 'Cold room temperature')], max_length=500, null=True, verbose_name='storage type'),
        ),
        migrations.AddField(
            model_name='typesofseed',
            name='storage_type_rw',
            field=models.CharField(choices=[('RT', 'Room temperature'), ('CRT', 'Cold room temperature')], max_length=500, null=True, verbose_name='storage type'),
        ),
    ]
