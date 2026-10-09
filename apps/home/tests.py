from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.home import content
from apps.landing.models import Lead


class HomeViewTests(TestCase):
    def setUp(self):
        self.url = reverse('home:home')

    def test_returns_200_with_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

    def test_renders_theme_variables(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.THEME['color_primary'])

    def test_nav_has_only_home_tab_marked_as_current(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        self.assertEqual(html.count('aria-current="page"'), 1)
        self.assertContains(response, content.NAV['home_text'])

    def test_renders_intro_with_photo_placeholder(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.INTRO['headline'])
        self.assertContains(response, content.INTRO['photo_placeholder'])

    def test_renders_products_with_prices_and_features(self):
        response = self.client.get(self.url)
        for product in content.PRODUCTS:
            self.assertContains(response, product['name'])
            self.assertContains(response, product['price'])
            for feature in product['features']:
                self.assertContains(response, feature)

    def test_renders_team(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.TEAM_SECTION['title'])
        for member in content.TEAM:
            self.assertContains(response, member['name'])
            self.assertContains(response, member['role'])

    def test_renders_footer(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.FOOTER['text'])

    def test_does_not_link_to_landing(self):
        """La home y la landing son webs independientes: sin enlaces entre ellas."""
        response = self.client.get(self.url)
        self.assertNotContains(response, reverse('landing:home'))
        
    def test_support_plans_rendered(self):
        response = self.client.get(self.url)
        for plan in content.SUPPORT_PLANS:
            self.assertContains(response, plan['name'])
            self.assertContains(response, plan['price'])
            for feature in plan['features']:
                self.assertContains(response, feature)

    def test_tech_partner_links_to_its_site_in_new_tab(self):
        partner = {**content.TECH_PARTNER, 'url': 'https://orion.example/'}
        with patch.dict(content.TECH_PARTNER, partner):
            response = self.client.get(self.url)
        self.assertContains(response, 'href="https://orion.example/"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertContains(response, partner['new_tab_label'])

    def test_tech_partner_shows_logo_and_name(self):
        response = self.client.get(self.url)
        self.assertContains(response, content.TECH_PARTNER['logo'])
        self.assertContains(response, content.TECH_PARTNER['name'])

    def test_tech_partner_without_url_is_not_a_link(self):
        with patch.dict(content.TECH_PARTNER, {'url': ''}):
            response = self.client.get(self.url)
        self.assertContains(response, content.TECH_PARTNER['name'])
        self.assertNotContains(response, 'class="tech-partner" href=')

    def test_tech_section_rendered_above_team(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        self.assertContains(response, content.TECH_SECTION['title'])
        for item in content.TECH_ITEMS:
            self.assertContains(response, item['name'])
            self.assertContains(response, item['text'])
        self.assertLess(
            html.index(content.TECH_SECTION['title']),
            html.index(content.TEAM_SECTION['title']),
        )

    def test_product_buttons_link_to_contact_with_product(self):
        response = self.client.get(self.url)
        for product in content.PRODUCTS:
            self.assertContains(
                response, f'href="{reverse("home:contact")}?producto={product["slug"]}"'
            )
        self.assertNotContains(response, 'mailto:' + content.CONTACT['email'] + '?subject=')

    def test_info_button_below_support_and_above_tech(self):
        response = self.client.get(self.url)
        html = response.content.decode()
        button = (
            f'href="{reverse("home:contact")}?producto={content.INFO_REQUEST["slug"]}">'
            f'{content.SUPPORT_SECTION["cta_text"]}</a>'
        )
        self.assertIn(button, html)
        self.assertLess(html.index('id="soporte"'), html.index(button))
        self.assertLess(html.index(button), html.index('id="tecnologia"'))


class ContactViewGetTests(TestCase):
    def setUp(self):
        self.url = reverse('home:contact')

    def test_returns_200_with_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/contact.html')
        self.assertContains(response, content.CONTACT_FORM['submit_text'])

    def test_h1_depends_on_the_button_pressed(self):
        for request in content.contact_requests():
            html = self.client.get(self.url + f'?producto={request["slug"]}').content.decode()
            self.assertEqual(html.count('<h1'), 1)
            self.assertIn(f'<h1>{request["contact_heading"]}</h1>', html)

    def test_product_is_a_hidden_field_set_by_the_button(self):
        response = self.client.get(self.url + '?producto=implementacion')
        self.assertContains(
            response, '<input type="hidden" name="product" value="implementacion"', html=False
        )
        self.assertNotContains(response, '<select name="product"')

    def test_without_or_with_unknown_product_it_is_an_info_request(self):
        for query in ('', '?producto=no-existe'):
            response = self.client.get(self.url + query)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'<h1>{content.INFO_REQUEST["contact_heading"]}</h1>')
            self.assertContains(response, 'name="product" value="informacion"')

    def test_form_has_its_own_fields_and_not_the_landing_service(self):
        response = self.client.get(self.url)
        for field in ('product', 'phone', 'contact_preference', 'website'):
            self.assertContains(response, f'name="{field}"')
        self.assertNotContains(response, 'name="service_interest"')

    def test_links_back_to_home(self):
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{reverse("home:home")}"')
        self.assertNotContains(response, reverse('landing:home'))


class ContactViewPostTests(TestCase):
    def setUp(self):
        # El formulario se envía a la misma URL con la que se abrió la página.
        self.url = reverse('home:contact') + '?producto=diagnostico'
        self.data = {
            'product': 'diagnostico',
            'name': 'Ana Pérez',
            'email': 'ana@empresa.com',
            'phone': '+34 600 000 000',
            'company': 'Empresa SA',
            'contact_preference': 'videollamada',
            'message': 'Quiero un diagnóstico.',
            'website': '',
        }

    def ajax_post(self, data):
        return self.client.post(self.url, data, headers={'x-requested-with': 'XMLHttpRequest'})

    def test_valid_post_creates_contact_lead_and_redirects(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url + '#contacto')
        lead = Lead.objects.get()
        self.assertEqual(lead.source, Lead.Source.CONTACT)
        self.assertEqual(lead.product, 'diagnostico')
        self.assertEqual(lead.phone, '+34 600 000 000')
        self.assertEqual(lead.contact_preference, 'videollamada')
        self.assertEqual(lead.service_interest, '')

    def test_source_cannot_be_forged_from_the_form(self):
        self.client.post(self.url, {**self.data, 'source': Lead.Source.LANDING})
        self.assertEqual(Lead.objects.get().source, Lead.Source.CONTACT)

    def test_valid_ajax_post_returns_contact_success_message(self):
        response = self.ajax_post(self.data)
        self.assertEqual(
            response.json(), {'ok': True, 'message': content.CONTACT_FORM['success_message']}
        )

    def test_info_request_is_saved_as_its_product(self):
        url = reverse('home:contact') + '?producto=informacion'
        self.client.post(url, {**self.data, 'product': 'informacion'})
        self.assertEqual(Lead.objects.get().product, 'informacion')

    def test_tampered_or_missing_product_is_rejected(self):
        for product in ('', 'no-existe'):
            response = self.ajax_post({**self.data, 'product': product})
            self.assertEqual(response.status_code, 400)
            errors = response.json()['errors']['product']
            self.assertEqual(errors[0]['message'], content.CONTACT_FORM['invalid_request'])
        self.assertEqual(Lead.objects.count(), 0)

    def test_tampered_product_error_is_shown_without_js(self):
        response = self.client.post(self.url, {**self.data, 'product': 'no-existe'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, content.CONTACT_FORM['invalid_request'])

    def test_phone_and_preference_are_optional(self):
        response = self.ajax_post({**self.data, 'phone': '', 'contact_preference': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 1)

    def test_invalid_contact_preference_is_rejected(self):
        response = self.ajax_post({**self.data, 'contact_preference': 'paloma'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('contact_preference', response.json()['errors'])

    def test_honeypot_fakes_success_and_creates_nothing(self):
        response = self.client.post(self.url, {**self.data, 'website': 'http://spam.example'})
        self.assertRedirects(response, self.url + '#contacto')
        self.assertEqual(Lead.objects.count(), 0)

    @override_settings(LEAD_THROTTLE_MAX=1)
    def test_throttle_is_shared_with_the_landing(self):
        Lead.objects.create(name='Previo', email='previo@empresa.com', ip_address='127.0.0.1')
        response = self.ajax_post(self.data)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Lead.objects.count(), 1)
