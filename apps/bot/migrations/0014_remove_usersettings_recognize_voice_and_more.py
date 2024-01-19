# Generated by Django 5.0 on 2024-01-19 10:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0013_remove_chat_gpt_preprompt_remove_chat_mentioning_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersettings',
            name='recognize_voice',
        ),
        migrations.AddField(
            model_name='chatsettings',
            name='recognize_voice',
            field=models.BooleanField(default=True, verbose_name='Распозновать голосовые автоматически'),
        ),
    ]
