# Generated by Django 3.2.13 on 2023-01-02 14:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0035_alter_meme_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notify',
            name='message_thread_id',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='message_thread_id'),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='message_thread_id',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='message_thread_id'),
        ),
    ]