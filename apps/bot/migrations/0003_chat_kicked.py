# Generated by Django 3.2.20 on 2023-10-28 19:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='kicked',
            field=models.BooleanField(default=True, verbose_name='Бота кикнули'),
        ),
    ]
