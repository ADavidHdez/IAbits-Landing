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


SITE = {
    'name': 'IAbits Studio',
    'tagline': 'Automatización con IA para tu negocio',
    'meta_description': (
        'Agencia de automatización con inteligencia artificial: agentes de '
        'ventas, automatización de procesos, bases de conocimiento, webs y '
        'redes sociales. Ahorra tiempo, dinero y personal.'
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
    'radius': '12px',
    'max_width': '1080px',
}

HERO = {
    'headline': 'Recupera cientos de horas al mes con agentes de IA trabajando para ti',
    'subheadline': (
        'Automatizamos ventas, procesos y conocimiento interno para que tu '
        'equipo se dedique a lo que genera ingresos. Sin ampliar plantilla.'
    ),
    'cta_text': 'Quiero mi diagnóstico gratuito',
    'cta_anchor': '#contacto',
}

SERVICES_SECTION = {
    'title': 'Qué podemos automatizar por ti',
    'subtitle': 'Soluciones de IA aplicadas a resultados, no a promesas.',
}

SERVICES = [
    Service(
        slug='agentes-outbound',
        icon='🤖',
        title='Agentes de IA para ventas outbound',
        description=(
            'Equipos de agentes autónomos que prospectan, cualifican y '
            'contactan clientes por ti, 24/7. Tu embudo nunca duerme.'
        ),
    ),
    Service(
        slug='automatizacion-procesos',
        icon='⚙️',
        title='Automatización inteligente de procesos',
        description=(
            'Automatizamos tus tareas repetitivas para que tu equipo se '
            'dedique a lo que genera ingresos, no a copiar y pegar.'
        ),
    ),
    Service(
        slug='base-conocimiento',
        icon='📚',
        title='Base de conocimiento con IA',
        description=(
            'Implementaremos una Base de Conocimiento con IA para que tus '
            'empleados reduzcan a la mitad el tiempo que pierden buscando '
            'información.'
        ),
    ),
    Service(
        slug='webs-landing',
        icon='🖥️',
        title='Webs y landing pages que venden',
        description=(
            'Diseñamos páginas rápidas y enfocadas en conversión: menos '
            'adorno, más clientes.'
        ),
    ),
    Service(
        slug='redes-sociales',
        icon='📣',
        title='Redes sociales en piloto automático',
        description=(
            'Automatizamos y optimizamos tu presencia en redes: publicaciones '
            'constantes y contenido optimizado sin dedicarle horas.'
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

STEPS_SECTION = {
    'title': 'Cómo trabajamos',
    'subtitle': 'De la primera llamada a la automatización funcionando.',
}

STEPS = [
    {
        'number': '1',
        'title': 'Diagnóstico gratuito',
        'text': (
            'Analizamos tus procesos y te decimos exactamente dónde estás '
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
        'Déjanos tus datos y te contactamos con un diagnóstico gratuito, '
        'sin compromiso.'
    ),
    'submit_text': 'Solicitar diagnóstico gratuito',
    'sending_text': 'Enviando…',
    'success_message': 'Gracias por tu interés. Te contactaremos en menos de 24 horas.',
    'error_message': (
        'No hemos podido enviar tu solicitud. Inténtalo de nuevo en unos minutos.'
    ),
}

CONTACT = {
    'email': 'iabits.studio@gmail.com',
    'phone': '',
}

FOOTER = {
    'text': '© 2026 IAbits. Todos los derechos reservados.',
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
        'steps_section': STEPS_SECTION,
        'steps': STEPS,
        'form_section': FORM_SECTION,
        'contact': CONTACT,
        'footer': FOOTER,
    }
