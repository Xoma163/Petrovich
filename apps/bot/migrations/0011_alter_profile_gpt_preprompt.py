# Generated by Django 3.2.20 on 2023-12-05 08:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0010_alter_chat_gpt_preprompt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gpt_preprompt',
            field=models.TextField(default='', verbose_name='ChatGPT preprompt'),
        ),
    ]