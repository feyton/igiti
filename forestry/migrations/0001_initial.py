# Generated by Django 3.0.4 on 2020-04-09 17:55

import autoslug.fields
import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook', models.CharField(blank=True, max_length=255, verbose_name='author facebook')),
                ('twitter', models.CharField(blank=True, max_length=255, verbose_name='author twitter')),
                ('telephone', models.CharField(blank=True, max_length=13, verbose_name='telephone')),
                ('image', models.ImageField(blank=True, null=True, upload_to='author', verbose_name='Author Image')),
                ('bio', models.TextField(blank=True, verbose_name='author biography')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique=True, verbose_name='slug')),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog', verbose_name='image')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='text')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('published', models.BooleanField(default=False, verbose_name='published')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('pub_date', models.DateTimeField(blank=True, null=True, verbose_name='publish date')),
                ('featured', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='forestry.Author')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forestry.Category')),
            ],
            options={
                'verbose_name': 'blog post',
                'verbose_name_plural': 'blog posts',
                'ordering': ['pub_date'],
            },
        ),
    ]
