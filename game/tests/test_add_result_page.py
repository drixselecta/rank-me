from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()

class TestAddResultPage(TestCase):
    def test_form_validation(self):
        # create 2 users
        laurent = User.objects.create_user('laurent', 'laurent@test.com', 'pass')
        laurent.save()
        rolf = User.objects.create_user('rolf', 'rolf@test.com', 'pass')
        rolf.save()

        client = Client()

        # Unauthenticated users should be redirected to the login form to add a
        # result
        response = client.get('/results/add/')
        self.assertEqual(302, response.status_code)

        client.login(username='laurent', password='pass')
        response = client.get('/results/add/')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<form id="add-result')

        # test form validation

        # no user is specified
        response = client.post('/results/add/', {})
        self.assertFormError(response, 'form', 'loser', 'This field is required.')
        self.assertFormError(response, 'form', 'winner', 'This field is required.')

        # only winner is specified
        response = client.post('/results/add/', {'winner': laurent.id})
        self.assertFormError(response, 'form', 'loser', 'This field is required.')

        # winner and loser are the same user
        response = client.post('/results/add/', {'winner': laurent.id, 'loser': laurent.id})
        self.assertFormError(response, 'form', None, 'Winner and loser can\'t be the same player!')

        # no error should be redirected to results page
        response = client.post('/results/add/', {'winner': laurent.id, 'loser': rolf.id}, follow=True)
        self.assertRedirects(response, '/results/', 302, 200)