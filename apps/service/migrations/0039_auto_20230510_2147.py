# Generated by Django 3.2.13 on 2023-05-10 17:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0038_auto_20230510_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horoscopememe',
            name='meme_ptr',
        ),
        migrations.DeleteModel(
            name='Horoscope',
        ),
        migrations.DeleteModel(
            name='HoroscopeMeme',
        ),
    ]
