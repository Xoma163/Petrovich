# Generated by Django 3.1.12 on 2021-09-04 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_delete_statistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='notify',
            name='crontab',
            field=models.TextField(max_length=100, null=True, verbose_name='Crontab'),
        ),
    ]
