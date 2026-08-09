from django.test import Client, TestCase, override_settings
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

    def test_commented_out_sections_are_not_rendered(self):
        """La sintaxis {# #} solo comenta una línea: los bloques usan {% comment %}."""
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Social proof')
        self.assertNotContains(response, 'social-proof')


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

    def test_honeypot_post_fakes_success_and_creates_nothing(self):
        response = self.client.post(self.url, {**self.data, 'website': 'http://spam.example'})
        self.assertRedirects(response, self.url + '#contacto')
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

    def test_honeypot_post_fakes_success_and_creates_nothing(self):
        response = self.post({**self.data, 'website': 'http://spam.example'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Lead.objects.count(), 0)


class SecurityTests(TestCase):
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

    def test_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Lead.objects.count(), 0)

    def test_script_in_field_is_escaped_when_rerendered(self):
        payload = {**self.data, 'email': '', 'name': '<script>alert(1)</script>'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_admin_requires_authentication(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_lead_stores_client_ip_and_user_agent(self):
        self.client.post(
            self.url,
            self.data,
            HTTP_X_FORWARDED_FOR='203.0.113.7, 10.0.0.2',
            HTTP_USER_AGENT='NavegadorPrueba/1.0',
        )
        lead = Lead.objects.get()
        self.assertEqual(lead.ip_address, '203.0.113.7')
        self.assertEqual(lead.user_agent, 'NavegadorPrueba/1.0')


@override_settings(LEAD_THROTTLE_MAX=3, LEAD_THROTTLE_WINDOW_MINUTES=60)
class LeadThrottleTests(TestCase):
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

    def post(self, ajax=False, ip='203.0.113.7'):
        headers = {'x-requested-with': 'XMLHttpRequest'} if ajax else {}
        return self.client.post(self.url, self.data, headers=headers, REMOTE_ADDR=ip)

    def test_post_over_limit_same_ip_is_throttled(self):
        for _ in range(3):
            self.post()
        response = self.post(ajax=True)
        self.assertEqual(response.status_code, 429)
        self.assertIn('__all__', response.json()['errors'])
        self.assertEqual(Lead.objects.count(), 3)

    def test_throttled_classic_post_redirects_without_creating(self):
        for _ in range(3):
            self.post()
        response = self.post()
        self.assertRedirects(response, self.url + '#contacto')
        self.assertEqual(Lead.objects.count(), 3)

    def test_other_ip_not_affected(self):
        for _ in range(3):
            self.post()
        response = self.post(ip='198.51.100.9')
        self.assertRedirects(response, self.url + '#contacto')
        self.assertEqual(Lead.objects.count(), 4)

    def test_x_forwarded_for_first_ip_wins(self):
        for _ in range(4):
            self.client.post(
                self.url, self.data, HTTP_X_FORWARDED_FOR='203.0.113.7, 10.0.0.2'
            )
        self.assertEqual(Lead.objects.count(), 3)
