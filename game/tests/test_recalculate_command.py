from django.core.management import call_command
from django.test import TestCase
from trueskill import Rating, rate_1vs1

from ..models import Game
from .factories import UserFactory


class RecalculateCommandTestCase(TestCase):
    def test_recalculate(self):
        """
        Test the recalculate command.
        """
        users = [UserFactory(), UserFactory()]

        Game.objects.announce(users[0], users[1])
        Game.objects.announce(users[0], users[1])
        game = Game.objects.last()

        args = [25, 8]
        opts = {}
        call_command('recalculate', *args, **opts)

        winner_score, loser_score = rate_1vs1(
            Rating(25, 8), Rating(25, 8)
        )
        winner_score, loser_score = rate_1vs1(
            Rating(winner_score.mu, winner_score.sigma),
            Rating(loser_score.mu, loser_score.sigma)
        )

        self.assertEqual(game.winner.score, winner_score.mu)
        self.assertEqual(game.winner.stdev, winner_score.sigma)
        self.assertEqual(game.loser.score, loser_score.mu)
        self.assertEqual(game.loser.stdev, loser_score.sigma)