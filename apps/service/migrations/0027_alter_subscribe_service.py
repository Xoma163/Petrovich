# Generated by Django 3.2.12 on 2022-05-14 18:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0026_auto_20220514_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='service',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'YouTube'), (2, 'The hole'), (3, 'WASD')],
                                           default=1, verbose_name='Сервис'),
        ),
    ]