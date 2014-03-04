import operator
from trueskill import Rating, rate_1vs1

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.db.models import Q


class TeamManager(models.Manager):
    def get_score_board(self):
        return (self.get_query_set().order_by('-score')
                .prefetch_related('users'))

    def get_or_create_from_players(self, player_ids):
        """
        Return the team associated to the given players, creating it first if
        it doesn't exist.

        Args:
            player_ids: a tuple of user ids, or a single user id.
        """
        if not isinstance(player_ids, tuple):
            player_ids = (player_ids,)

        # We need to get only the teams that have the exact number of player
        # ids, otherwise we would also get teams that have the given players
        # plus additional ones
        team = self.annotate(c=models.Count('users')).filter(c=len(player_ids))

        # Chain filter over all player ids
        for player_id in player_ids:
            team = team.filter(users=player_id)

        if not team:
            created = True
            team = self.create()

            for player_id in player_ids:
                team.users.add(player_id)
        else:
            created = False
            team = team.get()

        return (team, created)


class Team(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='teams')
    score = models.FloatField('skills', default=25)
    stdev = models.FloatField('standard deviation', default=8.33)
    wins = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)

    objects = TeamManager()

    def get_name(self):
        return u" / ".join([user.username for user in self.users.all()])

    def __unicode__(self):
        return self.get_name()


class GameManager(models.Manager):
    def get_latest(self):
        return (self.get_query_set()
                .select_related('winner', 'loser')
                .prefetch_related('winner__users', 'loser__users')
                .order_by('-date')[:20])

    def announce(self, winner, loser):
        """
        Announce the results of a new game.

        Args:
            winner: the user id (or tuple of user ids) of the users who won the
            game.
            loser: the user id (or tuple of user ids) of the users who lost the
            game.
        """
        winner, created = Team.objects.get_or_create_from_players(winner)
        loser, created = Team.objects.get_or_create_from_players(loser)

        return self.create(winner=winner, loser=loser)


class Game(models.Model):
    winner = models.ForeignKey(Team, related_name='games_won')
    loser = models.ForeignKey(Team, related_name='games_lost')
    date = models.DateTimeField(default=timezone.now)

    objects = GameManager()

    def clean(self):
        if (self.winner_id is not None and self.loser_id is not None and
                self.winner_id == self.loser_id):
            raise ValidationError(
                "Winner and loser can't be the same team!"
            )

    def __unicode__(self):
        return u"%s beats %s" % (
            self.winner,
            self.loser
        )

    def update_score(self):
        winner = self.winner
        loser = self.loser

        winner_new_score, loser_new_score = rate_1vs1(
            Rating(winner.score, winner.stdev),
            Rating(loser.score, loser.stdev)
        )

        winner.score = winner_new_score.mu
        winner.stdev = winner_new_score.sigma
        winner.wins = winner.wins + 1
        winner.save()

        loser.score = loser_new_score.mu
        loser.stdev = loser_new_score.sigma
        loser.defeats = loser.defeats + 1
        loser.save()

        HistoricalScore.objects.create(
            game=self,
            winner_score=winner.score,
            loser_score=loser.score,
        )


class HistoricalScoreManager(models.Manager):
    def get_latest(self, nb_games=50):
        return (self.get_queryset()
                .select_related('game', 'game__winner', 'game__loser')
                .order_by('-id')[:nb_games])

    def get_latest_results_by_team(self, nb_games=50):
        """
        Get nb_games latest scores for each team

        :param nb_games:int number of games
        :return:dict Dict with key=team and value=list of score objects

        {team_a: [{skill: xx, played: xx, game: game_id}, ...]}
        """
        scores_by_team = {}

        teams = Team.objects.all().select_related('winner', 'loser')

        scores = self.get_latest(nb_games)
        scores = sorted(scores, key=lambda score: score.id)
        for score in scores:
            all_skills_by_game = {}
            for team in teams:
                team_scores = scores_by_team.get(team, [])

                result = {'game': score.game.id}

                if team.id == score.game.winner_id:
                    result['skill'] = score.winner_score
                    result['win'] = True
                    result['played'] = True
                elif team.id == score.game.loser_id:
                    result['skill'] = score.loser_score
                    result['win'] = False
                    result['played'] = True
                else:
                    result['played'] = False
                    if len(team_scores) == 0:
                        result['skill'] = self.get_last_score_for_team(team, scores[0].game)
                    else:
                        result['skill'] = team_scores[-1]['skill']

                all_skills_by_game[team] = result['skill']

                team_scores.append(result)
                scores_by_team[team] = team_scores

            positions_for_game = sorted(all_skills_by_game.iteritems(), key=operator.itemgetter(1), reverse=True)
            for idx, position in enumerate(positions_for_game, start=1):
                scores_by_team[position[0]][-1]['position'] = idx

        return scores_by_team

    def get_last_score_for_team(self, team, game):
        """
        Returns the latest skill before game :game for team :team

        :param team:Team
        :param game:Game
        :return:skill
        """
        historical_score_id = game.historical_score.id
        last_score = (self.get_queryset()
                      .filter(Q(game__winner=team) | Q(game__loser=team))
                      .filter(id__lte=historical_score_id)
                      .select_related('game__winner', 'game__loser', 'game')
                      .order_by('-id')
                      .first())

        return last_score.winner_score if last_score.game.winner == team else last_score.loser_score


class HistoricalScore(models.Model):
    game = models.OneToOneField(Game, related_name='historical_score')
    winner_score = models.FloatField('Winner current score')
    loser_score = models.FloatField('Loser current score')

    objects = HistoricalScoreManager()
