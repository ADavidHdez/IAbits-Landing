"""Tests de SEO técnico: robots.txt, sitemap, favicon, canónica y JSON-LD."""
import json
import re
from xml.etree import ElementTree

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.common.seo import json_ld, price_amount
from apps.home import content as home_content
from apps.landing import content as landing_content

JSON_LD_RE = re.compile(
    r'<script type="application/ld\+json" nonce="[^"]+">(.*?)</script>', re.S
)


def extract_json_ld(response):
    """Devuelve el JSON-LD de la página ya parseado (falla si no es JSON válido)."""
    match = JSON_LD_RE.search(response.content.decode())
    assert match, 'La página no tiene bloque JSON-LD con nonce'
    return json.loads(match.group(1))


class RobotsTxtTests(TestCase):
    def setUp(self):
        self.response = self.client.get('/robots.txt')
        self.body = self.response.content.decode()

    def test_es_texto_plano(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(self.response['Content-Type'].startswith('text/plain'))

    def test_permite_la_web_y_bloquea_login_y_chat(self):
        self.assertIn('Allow: /\n', self.body)
        self.assertIn('Disallow: /accounts/\n', self.body)
        self.assertIn(f'Disallow: {reverse("landing:chat")}\n', self.body)

    def test_enlaza_el_sitemap_con_url_absoluta(self):
        self.assertIn('Sitemap: http://testserver/sitemap.xml', self.body)

    def test_no_revela_la_ruta_del_admin(self):
        self.assertNotIn(settings.ADMIN_URL, self.body)


class SitemapTests(TestCase):
    def test_lista_las_paginas_publicas_con_urls_absolutas(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        tree = ElementTree.fromstring(response.content)
        locs = [loc.text for loc in tree.findall('s:url/s:loc', ns)]
        self.assertEqual(
            locs,
            ['http://testserver' + reverse('home:home'),
             'http://testserver' + reverse('home:contact'),
             'http://testserver' + reverse('landing:home')],
        )

    def test_usa_el_esquema_de_la_peticion(self):
        response = self.client.get('/sitemap.xml', secure=True)
        self.assertContains(response, '<loc>https://testserver/</loc>')


class FaviconTests(TestCase):
    def test_favicon_ico_redirige_al_estatico(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('img/favicon.ico'))

    def test_las_paginas_declaran_su_icono(self):
        for url in (reverse('home:home'), reverse('home:contact'), reverse('landing:home')):
            self.assertContains(self.client.get(url), 'rel="icon"')


class PublicPagesSeoTests(TestCase):
    """Comprobaciones comunes a la home, la página de contacto y la landing."""

    pages = (
        ('home:home', home_content.SITE),
        ('home:contact', home_content.CONTACT_SITE),
        ('landing:home', landing_content.SITE),
    )

    def test_titulos_y_descripciones_distintos_entre_paginas(self):
        titles = [site['title'] for _, site in self.pages]
        descriptions = [site['meta_description'] for _, site in self.pages]
        self.assertEqual(len(set(titles)), len(titles))
        self.assertEqual(len(set(descriptions)), len(descriptions))

    def test_longitudes_de_titulo_y_descripcion(self):
        """Por encima de estos límites Google corta el texto en los resultados."""
        for _, site in self.pages:
            self.assertLessEqual(len(site['title']), 60, site['title'])
            self.assertLessEqual(len(site['meta_description']), 158, site['meta_description'])

    def test_title_y_meta_description_renderizados(self):
        for name, site in self.pages:
            response = self.client.get(reverse(name))
            self.assertContains(response, f'<title>{site["title"]}</title>')
            self.assertContains(
                response, f'<meta name="description" content="{site["meta_description"]}">'
            )

    def test_canonica_absoluta_sin_querystring(self):
        for name, _ in self.pages:
            url = reverse(name)
            response = self.client.get(url + '?utm_source=prueba')
            self.assertContains(
                response, f'<link rel="canonical" href="http://testserver{url}">'
            )
            self.assertNotContains(response, 'utm_source')

    def test_open_graph_y_twitter_card(self):
        for name, site in self.pages:
            url = reverse(name)
            response = self.client.get(url)
            for prop, value in (
                ('og:type', 'website'),
                ('og:site_name', landing_content.BRAND['name']),
                ('og:title', site['title']),
                ('og:description', site['meta_description']),
                ('og:url', f'http://testserver{url}'),
                ('og:locale', 'es_ES'),
            ):
                self.assertContains(response, f'<meta property="{prop}" content="{value}">')
            self.assertContains(response, '<meta name="twitter:card" content="summary">')
            self.assertRegex(
                response.content.decode(),
                r'<meta property="og:image" content="http://testserver/static/'
                + re.escape(landing_content.BRAND['social_image']) + '">',
            )

    def test_logo_con_alt_de_marca_y_medidas(self):
        brand = landing_content.BRAND
        for name, _ in self.pages:
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn(f'alt="{brand["name"]}"', html)
            self.assertIn(
                f'width="{brand["logo_width"]}" height="{brand["logo_height"]}"', html
            )
            self.assertNotIn('alt="Logo"', html)


class HomeJsonLdTests(TestCase):
    def setUp(self):
        self.data = extract_json_ld(self.client.get(reverse('home:home')))
        self.nodes = {node['@type']: node for node in self.data['@graph']}

    def test_organizacion_con_datos_de_contacto(self):
        business = self.nodes['ProfessionalService']
        self.assertEqual(business['name'], landing_content.BRAND['name'])
        self.assertEqual(business['url'], 'http://testserver/')
        self.assertTrue(business['logo'].startswith('http://testserver/static/'))
        self.assertEqual(business['email'], landing_content.CONTACT['email'])
        self.assertEqual(business['areaServed']['name'], 'España')

    def test_ofertas_con_precio_solo_si_es_exacto(self):
        offers = self.nodes['ProfessionalService']['makesOffer']
        self.assertEqual(len(offers), len(home_content.PRODUCTS))
        for offer, product in zip(offers, home_content.PRODUCTS):
            self.assertEqual(offer['itemOffered']['name'], product['name'])
            amount = price_amount(product['price'])
            if amount:
                self.assertEqual(offer['price'], amount)
                self.assertEqual(offer['priceCurrency'], 'EUR')
            else:
                self.assertNotIn('price', offer)

    def test_incluye_web_y_pagina(self):
        self.assertIn('WebSite', self.nodes)
        self.assertEqual(self.nodes['WebPage']['name'], home_content.SITE['title'])


class LandingJsonLdTests(TestCase):
    def test_organizacion_y_pagina(self):
        data = extract_json_ld(self.client.get(reverse('landing:home')))
        nodes = {node['@type']: node for node in data['@graph']}
        self.assertEqual(nodes['Organization']['name'], landing_content.BRAND['name'])
        page = nodes['WebPage']
        self.assertEqual(page['url'], 'http://testserver' + reverse('landing:home'))
        self.assertEqual(page['name'], landing_content.SITE['title'])
        self.assertEqual(page['about']['@id'], nodes['Organization']['@id'])


class ContactJsonLdTests(TestCase):
    def test_pagina_de_contacto_de_la_organizacion(self):
        data = extract_json_ld(self.client.get(reverse('home:contact')))
        nodes = {node['@type']: node for node in data['@graph']}
        page = nodes['ContactPage']
        self.assertEqual(page['url'], 'http://testserver' + reverse('home:contact'))
        self.assertEqual(page['name'], home_content.CONTACT_SITE['title'])
        self.assertEqual(page['about']['@id'], nodes['ProfessionalService']['@id'])


class JsonLdHelperTests(SimpleTestCase):
    def test_escapa_lo_que_podria_cerrar_el_script(self):
        data = {'name': '</script><script>alert(1)</script> & cía'}
        output = json_ld(data)
        self.assertNotIn('<', output)
        self.assertNotIn('>', output)
        self.assertNotIn('&', output)
        self.assertEqual(json.loads(output), data)

    def test_price_amount(self):
        self.assertEqual(price_amount('290 €'), '290')
        self.assertEqual(price_amount('1.500 €'), '1500')
        self.assertEqual(price_amount('1.500,50 €'), '1500.50')
        self.assertIsNone(price_amount('desde 1.500 €'))
        self.assertIsNone(price_amount(''))


class LoginNoIndexTests(TestCase):
    def test_login_no_indexable_y_sin_canonica(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertContains(response, '<meta name="robots" content="noindex">')
        self.assertNotContains(response, 'rel="canonical"')
