from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.home import content


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
