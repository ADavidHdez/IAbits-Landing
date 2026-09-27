"""Tests de apps/common/http.py."""
from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.common.http import get_client_ip


class GetClientIpTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def peticion(self, **meta):
        return self.factory.get('/', **meta)

    def test_sin_proxy_usa_remote_addr(self):
        request = self.peticion(REMOTE_ADDR='203.0.113.7')
        self.assertEqual(get_client_ip(request), '203.0.113.7')

    def test_usa_la_ultima_entrada_de_forwarded_for(self):
        request = self.peticion(
            HTTP_X_FORWARDED_FOR='203.0.113.7, 10.0.0.2', REMOTE_ADDR='127.0.0.1'
        )
        self.assertEqual(get_client_ip(request), '10.0.0.2')

    def test_valor_no_valido_cae_a_remote_addr(self):
        request = self.peticion(
            HTTP_X_FORWARDED_FOR='<script>alert(1)</script>', REMOTE_ADDR='203.0.113.7'
        )
        self.assertEqual(get_client_ip(request), '203.0.113.7')

    def test_descarta_el_puerto(self):
        request = self.peticion(HTTP_X_FORWARDED_FOR='10.0.0.2:51234')
        self.assertEqual(get_client_ip(request), '10.0.0.2')

    def test_acepta_ipv6(self):
        request = self.peticion(HTTP_X_FORWARDED_FOR='[2001:db8::1]:443')
        self.assertEqual(get_client_ip(request), '2001:db8::1')

    @override_settings(TRUSTED_PROXY_DEPTH=2)
    def test_con_dos_proxies_salta_una_entrada_mas(self):
        request = self.peticion(HTTP_X_FORWARDED_FOR='203.0.113.7, 10.0.0.2, 10.0.0.3')
        self.assertEqual(get_client_ip(request), '10.0.0.2')

    def test_sin_datos_devuelve_none(self):
        self.assertIsNone(get_client_ip(self.factory.get('/', REMOTE_ADDR='')))
