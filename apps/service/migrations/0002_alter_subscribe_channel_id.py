# Generated by Django 3.2.20 on 2023-10-14 20:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='channel_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ID канала'),
        ),
    ]