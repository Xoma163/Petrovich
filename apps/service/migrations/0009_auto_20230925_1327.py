# Generated by Django 3.2.20 on 2023-09-25 09:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0008_remove_subscribe_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscribe',
            name='is_stream',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='last_stream_status',
        ),
    ]