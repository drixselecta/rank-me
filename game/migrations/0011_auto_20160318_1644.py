# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-18 15:44
from __future__ import unicode_literals

from django.db import migrations


def game_teams_to_users(apps, schema_editor):
    Game = apps.get_model('game', 'Game')

    for game in Game.objects.all():
        game.winner_user = game.winner.users.first()
        game.loser_user = game.winner.users.first()
        game.save()


def score_teams_to_users(apps, schema_editor):
    Score = apps.get_model('game', 'Score')

    for score in Score.objects.all():
        score.user = score.team.users.first()
        score.save()


def historical_score_teams_to_users(apps, schema_editor):
    HistoricalScore = apps.get_model('game', 'HistoricalScore')

    for hs in HistoricalScore.objects.all():
        hs.user = hs.team.users.first()
        hs.save()


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20160318_1643'),
    ]

    operations = [
        migrations.RunPython(game_teams_to_users),
        migrations.RunPython(score_teams_to_users),
        migrations.RunPython(historical_score_teams_to_users),
    ]
