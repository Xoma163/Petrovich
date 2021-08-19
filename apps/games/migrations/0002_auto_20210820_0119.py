# Generated by Django 3.1.8 on 2021-08-19 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codenamesuser',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='codenamesuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tictactoesession',
            name='next_step',
        ),
        migrations.RemoveField(
            model_name='tictactoesession',
            name='user1',
        ),
        migrations.RemoveField(
            model_name='tictactoesession',
            name='user2',
        ),
        migrations.RemoveField(
            model_name='gamer',
            name='codenames_points',
        ),
        migrations.RemoveField(
            model_name='gamer',
            name='tic_tac_toe_points',
        ),
        migrations.DeleteModel(
            name='CodenamesSession',
        ),
        migrations.DeleteModel(
            name='CodenamesUser',
        ),
        migrations.DeleteModel(
            name='TicTacToeSession',
        ),
    ]
