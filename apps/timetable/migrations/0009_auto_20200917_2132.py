# Generated by Django 3.0.8 on 2020-09-17 17:32

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timetable', '0008_auto_20200917_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='week_number',
            field=models.CharField(
                choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                         ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'),
                         ('15', '15')], max_length=2, verbose_name='Номер недели'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='week_number2',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(choices=[], max_length=2, verbose_name='Номер недели 2'), default=list,
                size=None),
        ),
    ]
