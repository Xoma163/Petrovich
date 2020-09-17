# Generated by Django 3.0.8 on 2020-09-17 16:57

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timetable', '0006_lesson_week_number2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='week_number2',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(choices=[('1', '1 - нечётные'), ('2', '2 - чётные')], max_length=2,
                                            verbose_name='Номер недели'), default=list, size=None),
        ),
    ]
