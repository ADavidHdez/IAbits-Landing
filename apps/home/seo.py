"""Datos estructurados (schema.org) de la home."""
from apps.common.seo import json_ld, price_amount
from apps.landing.content import BRAND
from apps.landing.seo import home_url, organization, organization_id, web_page

from . import content


def offer(product) -> dict:
    data = {
        '@type': 'Offer',
        'itemOffered': {
            '@type': 'Service',
            'name': product['name'],
            'description': product['summary'],
        },
    }
    # Solo precios exactos: 'desde 1.500 €' publicado como 1500 sería falso.
    amount = price_amount(product['price'])
    if amount:
        data['price'] = amount
        data['priceCurrency'] = BRAND['currency']
    return data


def home_json_ld(request) -> str:
    business = organization(request, schema_type='ProfessionalService')
    business['description'] = content.SITE['meta_description']
    business['makesOffer'] = [offer(product) for product in content.PRODUCTS]
    website = {
        '@type': 'WebSite',
        '@id': home_url(request) + '#web',
        'url': home_url(request),
        'name': BRAND['name'],
        'inLanguage': BRAND['language'],
        'publisher': {'@id': organization_id(request)},
    }
    return json_ld({
        '@context': 'https://schema.org',
        '@graph': [business, website, web_page(request, content.SITE)],
    })


def contact_json_ld(request) -> str:
    page = web_page(request, content.CONTACT_SITE)
    page['@type'] = 'ContactPage'
    return json_ld({
        '@context': 'https://schema.org',
        '@graph': [organization(request, schema_type='ProfessionalService'), page],
    })
