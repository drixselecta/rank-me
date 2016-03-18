# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-18 15:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20160318_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='teams',
        ),
        migrations.RemoveField(
            model_name='game',
            name='loser',
        ),
        migrations.RemoveField(
            model_name='game',
            name='winner',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='loser_user',
            new_name='loser',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='winner_user',
            new_name='winner',
        ),
        migrations.AlterField(
            model_name='game',
            name='loser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_lost', to='user.User'),
        ),
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_won', to='user.User'),
        ),
        migrations.AlterField(
            model_name='historicalscore',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historical_scores', to='user.User'),
        ),
        migrations.AlterField(
            model_name='score',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='user.User'),
        ),
        migrations.AlterUniqueTogether(
            name='historicalscore',
            unique_together=set([('user', 'game', 'competition')]),
        ),
        migrations.RemoveField(
            model_name='historicalscore',
            name='team',
        ),
        migrations.AlterUniqueTogether(
            name='score',
            unique_together=set([('competition', 'user')]),
        ),
        migrations.RemoveField(
            model_name='score',
            name='team',
        ),
    ]
