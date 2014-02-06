from django.test import TestCase

from .factories import UserFactory
from ..models import Team


class TestTeamGetOrCreate(TestCase):
    @classmethod
    def setUp(self):
        # Create 4 dummy users
        self.users = [UserFactory() for id in range(4)]

    def assertUsersEqual(self, first, second):
        def users_to_id_list(users):
            return sorted([user.id for user in users])

        first_ids = users_to_id_list(first)
        second_ids = users_to_id_list(second)

        return len(first_ids) == len(second_ids) and first_ids == second_ids

    def test_team_creation(self):
        team, created = Team.objects.get_or_create_from_players(
            (self.users[0].id, self.users[1].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 1)
        self.assertUsersEqual(team.users.all(), self.users[0:2])

        team, created = Team.objects.get_or_create_from_players(
            self.users[0].id
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 2)
        self.assertUsersEqual(team.users.all(), [self.users[0]])

        team, created = Team.objects.get_or_create_from_players(
            self.users[1].id
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 3)
        self.assertUsersEqual(team.users.all(), [self.users[1]])

    def test_team_uniqueness(self):
        """
        Test that calling get_or_create_from_players on the same set of players
        creates the team and then just returns it.
        """
        team, created = Team.objects.get_or_create_from_players(
            (self.users[0].id, self.users[1].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 1)
        self.assertUsersEqual(team.users.all(), self.users[0:2])

        # Check that team (0, 1) is equal to team (0, 1)
        team, created = Team.objects.get_or_create_from_players(
            (self.users[0].id, self.users[1].id)
        )
        self.assertFalse(created)
        self.assertEqual(Team.objects.count(), 1)
        self.assertUsersEqual(team.users.all(), self.users[0:2])

        # Check that team (1, 0) is equal to team (0, 1)
        team, created = Team.objects.get_or_create_from_players(
            (self.users[1].id, self.users[0].id)
        )
        self.assertFalse(created)
        self.assertEqual(Team.objects.count(), 1)
        self.assertUsersEqual(team.users.all(), self.users[0:2])

        # Check that team (1, 2) is different from team (0, 1)
        team, created = Team.objects.get_or_create_from_players(
            (self.users[1].id, self.users[2].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 2)
        self.assertUsersEqual(team.users.all(), self.users[1:3])

    def test_team_overlap(self):
        """
        Test that an overlapping team (eg. (0, 1, 2) vs (0, 1)) is reported as
        a new team.
        """
        team, created = Team.objects.get_or_create_from_players(
            (self.users[0].id, self.users[1].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 1)
        self.assertUsersEqual(team.users.all(), self.users[0:2])

        # Check that team (0, 1, 2) is different from (0, 1)
        team, created = Team.objects.get_or_create_from_players(
            (self.users[0].id, self.users[1].id, self.users[2].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 2)
        self.assertUsersEqual(team.users.all(), self.users[0:3])

        # Check that team (1, 2) is different from (0, 1, 2)
        team, created = Team.objects.get_or_create_from_players(
            (self.users[1].id, self.users[2].id)
        )
        self.assertTrue(created)
        self.assertEqual(Team.objects.count(), 3)
        self.assertUsersEqual(team.users.all(), self.users[1:3])