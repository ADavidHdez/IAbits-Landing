from django.test import TestCase
from django.urls import reverse

from apps.landing import content as landing_content

from . import content

PAGES = (
    ('legal:notice', content.LEGAL_NOTICE),
    ('legal:privacy', content.PRIVACY),
    ('legal:cookies', content.COOKIES),
)


class LegalPagesTests(TestCase):
    def test_pages_render_heading_sections_and_date(self):
        for name, page in PAGES:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'<h1>{page["heading"]}</h1>')
            self.assertContains(response, content.UPDATED)
            for section in page['sections']:
                self.assertContains(response, f'<h2>{section["title"]}</h2>')

    def test_pages_are_noindex_without_canonical(self):
        for name, _ in PAGES:
            response = self.client.get(reverse(name))
            self.assertContains(response, '<meta name="robots" content="noindex, follow">')
            self.assertNotContains(response, 'rel="canonical"')

    def test_seo_lengths(self):
        """Mismos límites que el resto de páginas, aunque no se indexen."""
        for _, page in PAGES:
            self.assertLessEqual(len(page['site']['title']), 60, page['site']['title'])
            self.assertLessEqual(
                len(page['site']['meta_description']), 158, page['site']['meta_description']
            )

    def test_notice_and_privacy_identify_the_owner(self):
        for name in ('legal:notice', 'legal:privacy'):
            response = self.client.get(reverse(name))
            for key in ('name', 'nif', 'address', 'phone'):
                self.assertContains(response, content.OWNER[key])
            self.assertContains(
                response, f'<a href="mailto:{content.OWNER["email"]}">'
            )

    def test_privacy_lists_retention_and_providers(self):
        response = self.client.get(reverse('legal:privacy'))
        for period in content.RETENTION.values():
            self.assertContains(response, period)
        for provider in ('Hostinger', 'Airtable', 'OpenRouter'):
            self.assertContains(response, provider)
        self.assertContains(response, 'href="https://www.aepd.es"')

    def test_does_not_link_to_either_site(self):
        """Comunes a la home y a la landing: no deben unir las dos webs."""
        response = self.client.get(reverse('legal:privacy'))
        self.assertNotContains(response, f'href="{reverse("home:home")}"')
        self.assertNotContains(response, f'href="{reverse("landing:home")}"')


class LegalLinksTests(TestCase):
    def test_public_pages_link_the_three_documents_in_the_footer(self):
        for url in (
            reverse('home:home'), reverse('home:contact'), reverse('landing:home'),
            reverse('legal:notice'),
        ):
            response = self.client.get(url)
            self.assertContains(response, 'class="footer-legal"')
            for link in content.FOOTER_LINKS:
                self.assertContains(response, f'href="{reverse(link["url_name"])}"')

    def test_current_legal_page_is_marked_in_the_footer(self):
        response = self.client.get(reverse('legal:cookies'))
        self.assertContains(
            response, f'<a href="{reverse("legal:cookies")}" aria-current="page">'
        )

    def test_forms_show_privacy_checkbox_and_basic_notice(self):
        for url in (reverse('home:contact'), reverse('landing:home')):
            response = self.client.get(url)
            self.assertContains(response, 'type="checkbox" name="privacy"')
            self.assertContains(response, content.FORM_CONSENT['notice'])
            self.assertContains(response, f'href="{reverse("legal:privacy")}" target="_blank"')

    def test_chat_disclaimer_links_to_privacy(self):
        with self.settings(N8N_CHAT_WEBHOOK_URL='https://n8n.example/webhook/chat'):
            response = self.client.get(reverse('landing:home'))
        self.assertContains(response, landing_content.CHAT['privacy_link_text'])
        self.assertContains(response, 'class="chat-disclaimer"')
