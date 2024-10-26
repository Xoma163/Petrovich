# Generated by Django 5.1 on 2024-10-02 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0020_remove_chat_settings_remove_profile_settings_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatsettings',
            name='chat',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='settings', to='bot.chat', verbose_name='Чат'),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='settings', to='bot.profile', verbose_name='Профиль'),
        ),
    ]