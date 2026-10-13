from django.urls import reverse

from . import content


def legal(request):
    """Enlaces legales del pie y textos de la casilla de privacidad.

    Llegan a todas las plantillas porque los usan la home, /contacto/, la
    landing, el chat y las propias páginas legales.
    """
    return {
        'legal_links': [
            {'url': reverse(link['url_name']), 'text': link['text']}
            for link in content.FOOTER_LINKS
        ],
        'legal_links_label': content.FOOTER_LINKS_LABEL,
        'privacy_url': reverse('legal:privacy'),
        'form_consent': content.FORM_CONSENT,
    }
