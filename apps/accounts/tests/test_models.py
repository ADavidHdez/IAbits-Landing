from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import LoginAttempt


class UserModelTests(TestCase):
    def test_str_devuelve_el_username(self):
        user = get_user_model()(username='staff')
        self.assertEqual(str(user), 'staff')

    def test_usuario_nuevo_no_es_staff_por_defecto(self):
        user = get_user_model().objects.create_user(
            username='staff', password='clave-larga-y-segura-123'
        )
        self.assertFalse(user.is_staff)
        self.assertEqual(user.bio, '')


class LoginAttemptModelTests(TestCase):
    def test_str_identifica_usuario_e_ip(self):
        attempt = LoginAttempt(username='staff', ip_address='203.0.113.7')
        self.assertEqual(str(attempt), 'staff desde 203.0.113.7')

    def test_ordering_mas_recientes_primero(self):
        viejo = LoginAttempt.objects.create(username='a', ip_address='203.0.113.7')
        nuevo = LoginAttempt.objects.create(username='b', ip_address='203.0.113.7')
        self.assertEqual(list(LoginAttempt.objects.all()), [nuevo, viejo])
