from django.test import TestCase
from django.urls import reverse

from apps.landing import content
from apps.landing.models import Lead


class LandingViewGetTests(TestCase):
    def setUp(self):
        self.url = reverse('landing:home')

    def test_returns_200_with_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing/home.html')

    def test_renders_hero_and_services(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.HERO['headline'])
        for service in content.SERVICES:
            self.assertContains(response, service.title)

    def test_renders_theme_variables(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.THEME['color_primary'])


class LandingViewPostTests(TestCase):
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

    def test_valid_post_creates_lead_and_redirects(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.get()
        self.assertEqual(lead.email, 'ana@empresa.com')
        self.assertEqual(lead.message, 'Quiero una base de conocimiento.')
        self.assertRedirects(response, self.url + '#contacto')

    def test_valid_post_shows_success_message(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, content.FORM_SECTION['success_message'])

    def test_success_message_renders_below_the_form(self):
        response = self.client.post(self.url, self.data, follow=True)
        html = response.content.decode()
        self.assertLess(html.index('</form>'), html.index(content.FORM_SECTION['success_message']))

    def test_invalid_post_rerenders_with_content(self):
        response = self.client.post(self.url, {**self.data, 'email': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertContains(response, content.HERO['headline'])

    def test_honeypot_post_creates_nothing(self):
        response = self.client.post(self.url, {**self.data, 'website': 'http://spam.example'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)


class LandingViewAjaxPostTests(TestCase):
    """El formulario se envía por fetch() desde static/js/lead-form.js."""

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

    def post(self, data):
        return self.client.post(self.url, data, headers={'x-requested-with': 'XMLHttpRequest'})

    def test_valid_post_returns_json_without_redirect(self):
        response = self.post(self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(
            response.json(),
            {'ok': True, 'message': content.FORM_SECTION['success_message']},
        )
        self.assertEqual(Lead.objects.count(), 1)

    def test_invalid_post_returns_400_with_field_errors(self):
        response = self.post({**self.data, 'email': ''})
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload['ok'])
        self.assertIn('email', payload['errors'])
        self.assertEqual(Lead.objects.count(), 0)

    def test_honeypot_post_returns_400_and_creates_nothing(self):
        response = self.post({**self.data, 'website': 'http://spam.example'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('website', response.json()['errors'])
        self.assertEqual(Lead.objects.count(), 0)
