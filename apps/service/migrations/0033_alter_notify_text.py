# Generated by Django 3.2.13 on 2022-11-04 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0032_notify_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notify',
            name='text',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Текст/команда'),
        ),
    ]
