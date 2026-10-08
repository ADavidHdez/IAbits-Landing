"""Datos estructurados (schema.org) de la marca y de la landing.

La home reutiliza `organization()` y `web_page()` para que las dos páginas
describan la misma organización con el mismo @id.
"""
from django.urls import reverse

from apps.common.seo import absolute_static, canonical_url, json_ld

from . import content


def home_url(request) -> str:
    return request.build_absolute_uri(reverse('home:home'))


def organization_id(request) -> str:
    return home_url(request) + '#organizacion'


def organization(request, schema_type='Organization') -> dict:
    data = {
        '@type': schema_type,
        '@id': organization_id(request),
        'name': content.BRAND['name'],
        'url': home_url(request),
        'logo': absolute_static(request, content.BRAND['logo']),
        'areaServed': {'@type': 'Country', 'name': content.BRAND['area_served']},
    }
    if content.CONTACT['email']:
        data['email'] = content.CONTACT['email']
    if content.CONTACT['phone']:
        data['telephone'] = content.CONTACT['phone']
    return data


def web_page(request, site) -> dict:
    url = canonical_url(request)
    return {
        '@type': 'WebPage',
        '@id': url + '#pagina',
        'url': url,
        'name': site['title'],
        'description': site['meta_description'],
        'inLanguage': content.BRAND['language'],
        'about': {'@id': organization_id(request)},
    }


def landing_json_ld(request) -> str:
    return json_ld({
        '@context': 'https://schema.org',
        '@graph': [organization(request), web_page(request, content.SITE)],
    })
