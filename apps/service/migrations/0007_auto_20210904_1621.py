# Generated by Django 3.1.12 on 2021-09-04 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0006_notify_crontab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notify',
            name='date',
            field=models.DateTimeField(null=True, verbose_name='Дата напоминания'),
        ),
    ]
