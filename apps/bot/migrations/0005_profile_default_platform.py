# Generated by Django 3.2.19 on 2023-05-15 04:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0004_alter_chat_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_platform',
            field=models.CharField(blank=True, max_length=20, verbose_name='asd'),
        ),
    ]
