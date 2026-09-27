from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import LoginAttempt

# El hasher de producción es lento a propósito; en los tests solo interesa que
# la contraseña case, y aquí se comprueban muchos intentos seguidos.
HASHER_RAPIDO = override_settings(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher']
)


@HASHER_RAPIDO
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


@HASHER_RAPIDO
@override_settings(LOGIN_THROTTLE_MAX=3, LOGIN_THROTTLE_WINDOW_MINUTES=15)
class LoginThrottleTests(TestCase):
    """Fuerza bruta contra /accounts/login/."""

    def setUp(self):
        self.url = reverse('accounts:login')
        self.password = 'clave-larga-y-segura-123'
        self.user = get_user_model().objects.create_user(
            username='staff', password=self.password
        )

    def fallar(self, ip='203.0.113.7'):
        return self.client.post(
            self.url, {'username': 'staff', 'password': 'incorrecta'}, REMOTE_ADDR=ip
        )

    def test_cada_fallo_queda_registrado(self):
        self.fallar()
        attempt = LoginAttempt.objects.get()
        self.assertEqual(attempt.username, 'staff')
        self.assertEqual(attempt.ip_address, '203.0.113.7')

    def test_pasado_el_limite_se_bloquea_la_ip(self):
        for _ in range(3):
            self.fallar()
        response = self.fallar()
        self.assertEqual(response.status_code, 429)

    def test_bloqueo_ignora_la_contrasena_correcta(self):
        """Bloqueada la IP, ni siquiera la clave buena entra: nada de oráculo."""
        for _ in range(3):
            self.fallar()
        response = self.client.post(
            self.url,
            {'username': 'staff', 'password': self.password},
            REMOTE_ADDR='203.0.113.7',
        )
        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_otra_ip_no_queda_bloqueada(self):
        for _ in range(3):
            self.fallar()
        response = self.client.post(
            self.url,
            {'username': 'staff', 'password': self.password},
            REMOTE_ADDR='198.51.100.9',
        )
        self.assertRedirects(response, '/')

    def test_login_correcto_limpia_el_contador(self):
        for _ in range(2):
            self.fallar()
        self.client.post(
            self.url,
            {'username': 'staff', 'password': self.password},
            REMOTE_ADDR='203.0.113.7',
        )
        self.assertEqual(LoginAttempt.objects.filter(ip_address='203.0.113.7').count(), 0)
