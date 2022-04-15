from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.apps.authentication.schemas import UserSchema


class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('homer', 'homer@simpson.com', 'homerpassword')
        self.user_json = UserSchema(username='homer', password='homerpassword').dict()
        self.wrong_credentials_json = UserSchema(username='homer', password='wrongpassword').dict()

    def test_login_existing_user_returns_ok(self):
        response = self.client.post(
            '/api/authentication/login',
            self.user_json,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_credentials_returns_unauthorized(self):
        response = self.client.post(
            '/api/authentication/login',
            self.wrong_credentials_json,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_status_logged_in_returns_ok(self):
        self.client.post(
            '/api/authentication/login',
            self.user_json,
            content_type='application/json'
        )
        response = self.client.get('/api/authentication/status')
        self.assertEqual(response.status_code, 200)

    def test_status_not_logged_in_returns_unauthorized(self):
        response = self.client.get('/api/authentication/status')
        self.assertEqual(response.status_code, 401)


