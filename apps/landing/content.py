"""Configuración de contenido de la landing page.

Este archivo es la ÚNICA fuente de textos, servicios, colores y datos de
contacto de la landing. Para cambiar cualquier cosa de la página, edita
los valores de aquí — no hace falta tocar templates, CSS ni base de datos.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    slug: str
    icon: str
    title: str
    description: str


# Datos de marca comunes a todas las páginas (home, landing y login). Llegan a
# las plantillas como `brand` por el context processor de apps/landing.
# 'logo_width'/'logo_height' son las medidas reales del PNG: si se cambia el
# logo, hay que actualizarlas para que el navegador reserve bien su hueco.
BRAND = {
    'name': 'IAbits Studio',
    'logo': 'img/logo-trimmed.png',
    'logo_width': 434,
    'logo_height': 321,
    # PROVISIONAL: falta una imagen social propia de 1200×630; mientras, el logo.
    'social_image': 'img/logo-trimmed.png',
    'social_image_width': 434,
    'social_image_height': 321,
    'locale': 'es_ES',
    'language': 'es-ES',
    'area_served': 'España',
    'currency': 'EUR',
}

# SEO de la landing: 'title' va al <title> y a Open Graph; 'meta_description'
# a la meta description y a Open Graph. Título ≤ 60 caracteres, descripción
# ≤ 158, o Google los corta.
SITE = {
    'name': BRAND['name'],
    'title': 'Automatiza procesos con IA en tu empresa | IAbits Studio',
    'meta_description': (
        'Recupera horas cada mes automatizando con IA las ventas y los procesos '
        'de tu empresa. Cuéntanos tu caso y te contactamos en menos de 24 h, '
        'sin compromiso.'
    ),
}

# Se inyecta como variables CSS en :root — main.css consume estos valores.
THEME = {
    'color_primary': '#1a56db',
    'color_primary_dark': '#1e429f',
    'color_bg': '#ffffff',
    'color_surface': '#f6f8fb',
    'color_text': '#111827',
    'color_muted': '#6b7280',
    'color_border': '#e5e7eb',
    # Avisos que piden atención, como el contador del botón del chat.
    'color_accent': '#e02424',
    'radius': '12px',
    'max_width': '1080px',
}

HERO = {
    'headline': 'Descubre qué procesos de tu negocio puedes automatizar con IA',
    'subheadline': (
        'Automatizamos tus ventas y tus procesos, y ordenamos tu conocimiento interno '
        'para que tu equipo se dedique a lo que genera ingresos. Sin ampliar plantilla.'
    ),
    'cta_text': 'Quiero más información',
    'cta_anchor': '#contacto',
}

SERVICES_SECTION = {
    'title': 'Qué podemos automatizar por ti',
    'subtitle': 'Soluciones de IA orientadas a resultados, no a promesas.',
}

SERVICES = [
    Service(
        slug='agentes-inbound',
        icon='🤖',
        title='Agentes de IA',
        description=(
            'Agentes autónomos que atienden a tus clientes, venden '
            'y ejecutan tareas por ti, 24/7.'
        ),
    ),
    Service(
        slug='automatizacion-procesos',
        icon='⚙️',
        title='Automatización inteligente',
        description=(
            'Tus tareas repetitivas se hacen solas, sin copiar y pegar ni '
            'errores. Tu equipo recupera horas cada semana.'
        ),
    ),
    Service(
        slug='base-conocimiento',
        icon='📚',
        title='Bases de conocimiento',
        description=(
            'Reunimos la información de tu empresa en un asistente con IA. '
            'Tu equipo pregunta y encuentra la respuesta al momento, sin perder '
            'tiempo buscando.'
        ),
    ),
    Service(
        slug='integraciones',
        icon='🔗',
        title='Integraciones inteligentes',
        description=(
            'Conectamos la IA con tu correo, tu CRM y las herramientas que ya '
            'usas para que trabajen juntas, sin errores ni datos duplicados.'
        ),
    ),
    Service(
        slug='webs-landing',
        icon='🖥️',
        title='Páginas web y landings',
        description=(
            'Diseñamos páginas rápidas y pensadas para que te contacten: menos '
            'adorno, más clientes.'
        ),
    ),
    Service(
        slug='redes-sociales',
        icon='📣',
        title='Redes sociales en piloto automático',
        description=(
            'Preparamos y programamos tus publicaciones con IA. Presencia '
            'constante en redes sin dedicarle horas.'
        ),
    ),
    Service(
        slug='software',
        icon='📐',
        title='Software a medida',
        description=(
            'Herramientas hechas para tu negocio, integradas con tus sistemas y '
            'adaptadas a tus procesos. Sin pagar por funciones que no necesitas.'
        ),
    ),
]

VALUE_PROPS_SECTION = {
    'title': 'Por qué automatizar con nosotros',
}

VALUE_PROPS = [
    {
        'title': 'Ahorra tiempo',
        'text': (
            'Las tareas que hoy consumen horas de tu equipo pasan a '
            'resolverse solas, en minutos y sin errores.'
        ),
    },
    {
        'title': 'Reduce costes',
        'text': (
            'Cada proceso automatizado es dinero que dejas de gastar en '
            'trabajo manual repetitivo.'
        ),
    },
    {
        'title': 'Escala sin contratar',
        'text': (
            'Atiende más clientes y más volumen de trabajo con el mismo '
            'equipo que tienes hoy.'
        ),
    },
]

# Llamada a la acción intermedia: recoge al visitante convencido por las
# ventajas antes de que siga leyendo cómo trabajamos.
MID_CTA = {
    'cta_text': 'Quiero más información',
    'cta_anchor': '#contacto',
}

STEPS_SECTION = {
    'title': 'Cómo trabajamos',
    'subtitle': 'De la primera llamada a la automatización funcionando.',
}

STEPS = [
    {
        'number': '1',
        'title': 'Diagnóstico de procesos',
        'text': (
            'Analizamos los procesos de tu negocio al detalle y te decimos exactamente dónde estás '
            'perdiendo tiempo y dinero.'
        ),
    },
    {
        'number': '2',
        'title': 'Diseño de la solución',
        'text': (
            'Te proponemos la automatización con mayor retorno, con plazos '
            'y resultados medibles.'
        ),
    },
    {
        'number': '3',
        'title': 'Implementación y soporte',
        'text': (
            'La ponemos en marcha, formamos a tu equipo y nos quedamos '
            'cerca para que siga funcionando.'
        ),
    },
]

FORM_SECTION = {
    'title': 'Cuéntanos qué quieres automatizar',
    'subtitle': (
        'Déjanos tus datos y te contactamos antes de 24 horas, '
        'sin ningún compromiso.'
    ),
    'submit_text': 'Solicitar información',
    'sending_text': 'Enviando…',
    'success_message': 'Gracias por tu interés. Te contactaremos en menos de 24 horas.',
    'error_message': (
        'No hemos podido enviar tu solicitud. Inténtalo de nuevo en unos minutos.'
    ),
}

# Chat flotante con el asistente de IA (responde un agente de n8n). Solo se
# muestra si N8N_CHAT_WEBHOOK_URL está configurada.
CHAT = {
    'title': 'IAbits Studio',
    'subtitle': 'Asistente de IAbits',
    'greeting': (
        '¡Hola! 👋 Soy el asistente de IAbits. Cuéntame qué te gustaría saber y veremos cómo podemos ayudarte.'
    ),
    'placeholder': 'Escribe tu mensaje…',
    'input_label': 'Tu mensaje',
    'disclaimer': 'Respuestas generadas por IA',
    # Enlace a /privacidad/ que sigue al aviso, en la misma línea.
    'privacy_link_text': 'Privacidad',
    'typing_label': 'El asistente está escribiendo…',
    'error_message': (
        'Ahora mismo no puedo responder. Déjanos tus datos en el formulario y '
        'te contactamos.'
    ),
    'throttle_message': (
        'Has enviado muchos mensajes seguidos. Si prefieres, usa el formulario '
        'y te contactamos.'
    ),
    'invalid_message': 'Escribe un mensaje de hasta 500 caracteres.',
    'form_link_text': 'Ir al formulario',
    'form_anchor': '#contacto',
    'open_label': 'Abrir chat',
    'close_label': 'Cerrar chat',
    'send_label': 'Enviar mensaje',
    # Burbuja que asoma sobre el botón a los pocos segundos (una vez por sesión)
    # y contador del botón: el saludo que espera dentro del chat.
    'teaser': '👋 ¿Te ayudo a automatizar algo de tu negocio?',
    'teaser_close_label': 'Cerrar aviso',
    'badge': '1',
}

CONTACT = {
    'email': 'contacto@iabits.tech',
    'phone': '',
}

FOOTER = {
    'text': '© 2026 IAbits Studio. Todos los derechos reservados.',
}


def service_choices():
    """Choices para el campo 'servicio de interés' del formulario de leads."""
    return [(s.slug, s.title) for s in SERVICES] + [('otro', 'Otro / no lo tengo claro')]


def get_landing_context():
    return {
        'site': SITE,
        'theme': THEME,
        'hero': HERO,
        'services_section': SERVICES_SECTION,
        'services': SERVICES,
        'value_props_section': VALUE_PROPS_SECTION,
        'value_props': VALUE_PROPS,
        'mid_cta': MID_CTA,
        'steps_section': STEPS_SECTION,
        'steps': STEPS,
        'form_section': FORM_SECTION,
        'chat': CHAT,
        'contact': CONTACT,
        'footer': FOOTER,
    }
