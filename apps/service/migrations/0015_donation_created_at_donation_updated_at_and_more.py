# Generated by Django 5.0.4 on 2024-05-26 07:41

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0014_rename_donations_donation'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='donation',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='gptpreprompt',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='gptpreprompt',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='gptusage',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='horoscopememe',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='horoscopememe',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='meme',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='meme',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='notify',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='notify',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='promocode',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='promocode',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='service',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='service',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='tag',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='tag',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='videocache',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='videocache',
            name='updated_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 551110, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='gptusage',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2024, 5, 26, 3, 41, 30, 550989, tzinfo=datetime.timezone.utc)),
        ),
    ]