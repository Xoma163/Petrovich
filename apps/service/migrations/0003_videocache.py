# Generated by Django 3.2.19 on 2023-06-02 18:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0002_alter_subscribe_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=100, verbose_name='ID канала')),
                ('video_id', models.CharField(max_length=100, null=True, verbose_name='ID видео')),
                ('file_id', models.CharField(max_length=128, verbose_name='file_id')),
                ('filename', models.CharField(max_length=256, verbose_name='Название файла')),
                ('video', models.FileField(blank=True, upload_to='service/video/', verbose_name='Видео')),
            ],
            options={
                'verbose_name': 'Кэш видео',
                'verbose_name_plural': 'Кэши видео',
                'ordering': ['filename'],
                'unique_together': {('channel_id', 'video_id')},
            },
        ),
    ]