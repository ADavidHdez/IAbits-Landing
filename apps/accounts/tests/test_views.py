from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:login')
        self.user = get_user_model().objects.create_user(
            username='staff', password='clave-larga-y-segura-123'
        )

    def test_login_page_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_valid_login_redirects_home(self):
        response = self.client.post(
            self.url, {'username': 'staff', 'password': 'clave-larga-y-segura-123'}
        )
        self.assertRedirects(response, '/')

    def test_invalid_login_rerenders_with_error(self):
        response = self.client.post(
            self.url, {'username': 'staff', 'password': 'incorrecta'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirects_home(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, '/')
