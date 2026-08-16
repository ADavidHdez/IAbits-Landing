import json
import urllib.error
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.landing import webhooks
from apps.landing.models import Lead

WEBHOOK_SETTINGS = {
    'N8N_WEBHOOK_URL': 'https://n8n.example/webhook/lead-landing',
    'N8N_WEBHOOK_TOKEN': 'token-de-prueba',
    'N8N_WEBHOOK_TIMEOUT': 5,
    'N8N_WEBHOOK_SOURCE': 'landing',
}


def fake_response(status=200):
    response = MagicMock()
    response.status = status
    response.__enter__.return_value = response
    return response


def make_lead(**overrides):
    data = {
        'name': 'Ana Pérez',
        'email': 'ana@empresa.com',
        'company': 'Empresa SA',
        'service_interest': 'base-conocimiento',
        'message': 'Quiero una base de conocimiento.',
        'ip_address': '203.0.113.7',
        'user_agent': 'NavegadorPrueba/1.0',
    }
    return Lead.objects.create(**{**data, **overrides})


@override_settings(**WEBHOOK_SETTINGS)
class SendLeadTests(TestCase):
    def test_posts_json_payload_with_token_header(self):
        lead = make_lead()
        with patch('apps.landing.webhooks.urllib.request.urlopen') as urlopen:
            urlopen.return_value = fake_response()
            self.assertTrue(webhooks.send_lead(lead))

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, WEBHOOK_SETTINGS['N8N_WEBHOOK_URL'])
        self.assertEqual(request.get_method(), 'POST')
        self.assertEqual(request.get_header('Content-type'), 'application/json')
        self.assertEqual(request.get_header('X-webhook-token'), 'token-de-prueba')
        self.assertEqual(urlopen.call_args.kwargs['timeout'], 5)

        payload = json.loads(request.data)
        self.assertEqual(payload['event'], 'lead.created')
        self.assertEqual(payload['source'], 'landing')
        self.assertEqual(payload['lead']['id'], str(lead.id))
        self.assertEqual(payload['lead']['email'], 'ana@empresa.com')
        self.assertEqual(payload['lead']['service_label'], 'Base de conocimiento con IA')
        self.assertEqual(payload['lead']['ip_address'], '203.0.113.7')

    def test_marks_lead_as_delivered_on_success(self):
        lead = make_lead()
        with patch('apps.landing.webhooks.urllib.request.urlopen') as urlopen:
            urlopen.return_value = fake_response()
            webhooks.send_lead(lead)

        lead.refresh_from_db()
        self.assertIsNotNone(lead.webhook_delivered_at)

    def test_http_error_is_swallowed_and_lead_stays_undelivered(self):
        lead = make_lead()
        error = urllib.error.HTTPError(
            WEBHOOK_SETTINGS['N8N_WEBHOOK_URL'], 500, 'Server Error', {}, None
        )
        with patch('apps.landing.webhooks.urllib.request.urlopen', side_effect=error):
            self.assertFalse(webhooks.send_lead(lead))

        lead.refresh_from_db()
        self.assertIsNone(lead.webhook_delivered_at)

    def test_connection_error_is_swallowed(self):
        lead = make_lead()
        with patch(
            'apps.landing.webhooks.urllib.request.urlopen',
            side_effect=urllib.error.URLError('sin conexión'),
        ):
            self.assertFalse(webhooks.send_lead(lead))

        lead.refresh_from_db()
        self.assertIsNone(lead.webhook_delivered_at)


class WebhookDisabledTests(TestCase):
    @override_settings(N8N_WEBHOOK_URL='')
    def test_no_request_when_url_is_empty(self):
        lead = make_lead()
        with patch('apps.landing.webhooks.urllib.request.urlopen') as urlopen:
            self.assertFalse(webhooks.send_lead(lead))
        urlopen.assert_not_called()

    @override_settings(N8N_WEBHOOK_URL='file:///etc/passwd')
    def test_non_http_scheme_is_rejected(self):
        self.assertFalse(webhooks.is_enabled())


@override_settings(**WEBHOOK_SETTINGS)
class LandingViewWebhookTests(TestCase):
    """El POST del formulario dispara el webhook tras confirmar la transacción."""

    def setUp(self):
        self.url = reverse('landing:home')
        self.data = {
            'name': 'Ana Pérez',
            'email': 'ana@empresa.com',
            'company': 'Empresa SA',
            'service_interest': 'base-conocimiento',
            'message': 'Quiero una base de conocimiento.',
            'website': '',
        }

    def test_valid_post_sends_lead_to_n8n(self):
        with patch('apps.landing.webhooks.send_lead_async') as send:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.url, self.data)

        send.assert_called_once()
        self.assertEqual(send.call_args.args[0].pk, Lead.objects.get().pk)

    def test_honeypot_post_does_not_send_anything(self):
        with patch('apps.landing.webhooks.send_lead_async') as send:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.url, {**self.data, 'website': 'http://spam.example'})

        send.assert_not_called()

    def test_invalid_post_does_not_send_anything(self):
        with patch('apps.landing.webhooks.send_lead_async') as send:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.url, {**self.data, 'email': ''})

        send.assert_not_called()

    def test_form_still_succeeds_when_n8n_is_down(self):
        with patch(
            'apps.landing.webhooks.urllib.request.urlopen',
            side_effect=urllib.error.URLError('sin conexión'),
        ):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    self.url, self.data, headers={'x-requested-with': 'XMLHttpRequest'}
                )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Lead.objects.count(), 1)
