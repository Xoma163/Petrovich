# Generated by Django 3.2.7 on 2021-10-26 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_auto_20210904_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notify',
            name='attachments',
        ),
    ]