# Generated by Django 3.2.13 on 2022-08-12 06:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0028_alter_milanatranslate_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MilanaTranslate',
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='service',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'YouTube'), (2, 'The Hole'), (3, 'WASD')],
                                           default=1, verbose_name='Сервис'),
        ),
    ]