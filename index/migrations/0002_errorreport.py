# Generated by Django 3.0.4 on 2020-04-12 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, null=True)),
                ('message', models.TextField()),
                ('time_stamp', models.TimeField(auto_now_add=True)),
                ('sender_ip', models.GenericIPAddressField()),
                ('url', models.URLField(blank=True, null=True)),
                ('spam', models.BooleanField(default=False)),
            ],
        ),
    ]
