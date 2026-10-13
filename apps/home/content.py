"""Configuración de contenido de la web home.

Este archivo es la ÚNICA fuente de textos de la home, igual que
apps/landing/content.py lo es de la landing. Los colores y el contacto se
comparten con la landing para que las dos webs se vean como una sola marca.

Los valores marcados con «PROVISIONAL» son de relleno: hay que sustituirlos
por los reales antes de publicar.
"""
from apps.landing.content import BRAND, CHAT, CONTACT, THEME

# SEO de la home: mismas reglas que SITE en apps/landing/content.py (título
# ≤ 60 caracteres, descripción ≤ 158) y distintos de los de la landing.
SITE = {
    'name': BRAND['name'],
    'title': 'Agencia de automatización con IA para pymes | IAbits Studio',
    'meta_description': (
        'Agencia de automatización con IA para pymes: detectamos cuellos de '
        'botella, implementamos agentes de IA y formamos a tu equipo. '
        'Solicita tu diagnóstico.'
    ),
}

NAV = {
    'logo_alt': BRAND['name'],
    'home_text': 'Inicio',
    # Enlaces a las secciones de la home, en el orden de la página. 'anchor'
    # es el id de la <section> en home.html: si se cambia uno, cambia el otro.
    'sections': [
        {'anchor': 'automatizamos', 'text': 'Servicios'},
        {'anchor': 'planes', 'text': 'Planes'},
        {'anchor': 'soporte', 'text': 'Soporte'},
        {'anchor': 'equipo', 'text': 'Equipo'},
    ],
}

# Bloque 1: presentación del negocio.
INTRO = {
    # Etiqueta sobre el titular: no repite el titular, dice para quién trabajamos.
    'eyebrow': 'Agencia de automatización para pymes',
    'headline': 'Automatización con IA para llevar tu negocio al siguiente nivel.',
    'description': (
            'La inteligencia artificial no es el futuro: ya es el presente.\n'
            'Sin embargo, muchos negocios todavía no han dado el paso.\n\n'
            'En IAbits nos preocupamos por tu negocio. Detectamos sus cuellos de botella, '
            'diseñamos la solución, la ponemos en marcha y te enseñamos a usarla.'
        ),
    # Sin foto todavía: se muestra un hueco con este texto. Al tener la
    # imagen, se coloca en static/img/ y se rellena 'photo' con su ruta
    # relativa (por ejemplo 'img/presentacion.jpg').
    'photo': '',
    'photo_alt': 'Equipo de IAbits Studio trabajando',
    'photo_placeholder': 'Foto próximamente',
}

# Bloque 2: los dos productos que vende el negocio.
PRODUCTS_SECTION = {
    'title': 'Planes',
    'subtitle': 'Empieza por saber dónde puedes ganar tiempo. Después, lo hacemos realidad.',
}

PRODUCTS = [
    {
        'slug': 'diagnostico',
        'name': 'Diagnóstico',
        'summary': 'Analizamos tu negocio y te decimos qué automatizar primero.',
        'price': '150 €',  # PROVISIONAL
        'price_note': 'pago único',  # PROVISIONAL
        'features': [  # PROVISIONAL
            'Sesión de análisis',
            'Mapa de tus procesos actuales con la metodología de la norma ISO 9001:2015',
            'Lista priorizada de automatizaciones',
            'Estimación de horas y dinero ahorrados',
            'Informe final con hoja de ruta',
        ],
        'cta_text': 'Solicitar diagnóstico',
        # <h1> de /contacto/ cuando se llega desde este botón.
        'contact_heading': 'Solicita tu diagnóstico',
        'featured': True,
    },
    {
        'slug': 'implementacion',
        'name': 'Implementación',
        'summary': 'Ponemos en marcha la automatización y la dejamos funcionando.',
        'price': 'desde 500 €',  # PROVISIONAL
        'price_note': 'según alcance',  # PROVISIONAL
        'features': [  # PROVISIONAL
            'Desarrollo e integración con tus herramientas',
            'Agentes de IA y flujos automáticos a medida',
            'Formación para tu equipo',
            '30 días de soporte tras la entrega',
            'Descontamos el precio del Diagnóstico',
        ],
        'cta_text': 'Solicitar implementación',
        # Aclaración opcional, en pequeño bajo el botón.
        'cta_note': 'Para clientes con diagnóstico',
        'contact_heading': 'Solicita tu implementación',
        'featured': False,
    },
]

# Bajo cada precio de PRODUCTS y SUPPORT_PLANS. Si algún cliente puede ser un
# particular, la ley exige indicar que el precio es final, con impuestos.
PRICE_TAX_NOTE = 'Impuestos incluidos'

PRODUCTS_FEATURED_LABEL = 'Empieza por aquí'  # Etiqueta que acompaña al producto destacado en la home.
SUPPORT_FEATURED_LABEL = 'Recomendado'  # Ídem para el plan de soporte destacado.

# Bloque 3: Mantenimiento y soporte: se ofrece como servicio adicional a la implementación, no como producto independiente.

SUPPORT_SECTION = {
    'title': 'Soporte y mantenimiento',
    'subtitle': 'Realizamos el mantenimiento de tus automatizaciones y te damos soporte.',
    # Botón bajo los planes: lleva a /contacto/ como petición de información.
    'cta_text': 'Solicitar información',
}

SUPPORT_PLANS = [
    {
            'slug': 'estandar',
            'name': 'Estándar',
            'summary': 'Lo mínimo para mantener tus automatizaciones funcionando.',
            'price': '57 €',  # PROVISIONAL
            'price_note': '/ mes',
            'features': [  # PROVISIONAL
                'Mantenimiento básico de tus automatizaciones',
                'Actualizaciones de tus agentes de IA',
            ],
            'cta_text': '',
            'featured': False,
        },
    
    {
        'slug': 'premium', 
        'name': 'Premium', 
        'summary': 'Lo ideal para mantener tus automatizaciones sin preocupaciones.',
        'price': '97 €',
        'price_note': '/ mes', 
        'features': [
            'Mantenimiento de tus automatizaciones',
            'Actualizaciones de tus agentes de IA',
            'Revisiones de seguridad y optimizaciones periódicas'
        ], 
        'cta_text': '', 
        'featured': True
     },
    
    {
        'slug': 'advanced',  
        'name': 'Avanzado',
        'summary': 'La opción más completa para mantener tus automatizaciones al día.',
        'price': '130 €', 
        'price_note': 
        '/ mes', 
        'features': [
            'Mantenimiento avanzado de tus automatizaciones',
            'Actualizaciones de tus agentes de IA',
            'Revisiones de seguridad y optimizaciones periódicas',
            'Soporte prioritario',
            'Mejoras y nuevas implementaciones según tus necesidades'
        ], 
        'cta_text': '', 
        'featured':False
    },
]

# Bloque 4: la tecnología con la que trabajamos.
TECH_SECTION = {
    'title': 'Lo que automatizamos por ti',
    'subtitle': 'Potenciados por la tecnología de',
}

# Marca que acompaña al subtítulo, enlazada a su web. La CSP solo admite
# imágenes propias: el logo va en static/img/, nunca enlazado desde otra web.
# Es solo el emblema recortado del póster original, ya en círculo con las
# esquinas transparentes, y se pinta junto al nombre. Sin 'logo' queda solo el nombre, y sin 'url' la marca
# aparece sin enlace.
TECH_PARTNER = {
    'name': 'IA ORION',
    'url': 'https://iaorion.com/empresa/',
    'logo': 'img/iaorion.webp',
    'new_tab_label': '(se abre en una pestaña nueva)',
}

# Los mismos servicios que la landing (apps/landing/content.SERVICES), con
# textos propios. 'service' es el slug del servicio equivalente: un test
# comprueba que las dos páginas ofrecen exactamente los mismos.
TECH_ITEMS = [  # PROVISIONAL
    {
        'service': 'agentes-inbound',
        'name': 'Agentes de IA',
        'text': (
            'Asistentes que atienden a tus clientes, responden dudas y '
            'ejecutan tareas por ti a cualquier hora.'
        ),
    },
    {
        'service': 'automatizacion-procesos',
        'name': 'Automatización inteligente',
        'text': (
            'Las tareas repetitivas se hacen solas: datos, emails y facturas '
            'sin copiar y pegar ni errores.'
        ),
    },
    {
        'service': 'base-conocimiento',
        'name': 'Bases de conocimiento',
        'text': (
            'La información de tu empresa ordenada y consultable con IA, '
            'para que tu equipo encuentre respuestas en segundos.'
        ),
    },
    {
        'service': 'integraciones',
        'name': 'Integraciones inteligentes',
        'text': (
            'Enlazamos la IA con tu correo, tu CRM, tu web y el resto de los '
            'sistemas que ya usas para que trabajen juntos y sin errores.'
        ),
    },
    {
        'service': 'software',
        'name': 'Software a medida',
        'text': (
            'Herramientas a medida para tareas específicas de tu negocio, potenciadas '
            'con IA e integradas con los sistemas que ya usas.'
        ),
    },
    {
        'service': 'webs-landing',
        'name': 'Páginas web y landings',
        'text': (
            'Hechas desde cero, elegantes y profesionales, pensadas para dar '
            'visibilidad a tu negocio.'
        ),
    },
    {
        'service': 'redes-sociales',
        'name': 'Redes sociales en piloto automático',
        'text': (
            'Publicaciones constantes y contenido optimizado con IA para que tu '
            'marca esté presente sin dedicarle horas.'
        ),
    },
]

# Bloque 5: quién compone el negocio.
TEAM_SECTION = {
    'title': 'Quién está detrás',
    'subtitle': 'Un equipo, un objetivo: que la tecnología trabaje para ti.',
}

TEAM = [
    {
        'name': 'David Hernández',  # PROVISIONAL
        'role': 'Fundador · Especialista en automatización con IA',  # PROVISIONAL
        'bio': (  # PROVISIONAL
            'Técnico en Automatización y Robótica Industrial. '
            'Diseño e implemento automatizaciones con inteligencia artificial '
            'para pequeñas y medianas empresas. '
            'Mi equipo y yo te acompañamos de principio a fin: entendemos cómo trabajas, '
            'pensamos la solución con más retorno y nos aseguramos de que funcione en el '
            'día a día.'
        ),
        'photo': 'img/david-hernandez.jpg',  # Igual que INTRO['photo']: ruta dentro de static/.
        # Encuadre de la foto dentro del círculo:
        # - photo_zoom: 1 = foto entera; 1.3 = 30 % más cerca.
        # - photo_focus: punto que queda fijo al acercar, como "X% Y%"
        #   ('50% 0%' = arriba al centro, '50% 50%' = centro exacto).
        'photo_zoom': 1.0,
        'photo_focus': '50% 20%',
        'photo_placeholder': 'Foto próximamente',
    },
]

FOOTER = {
    'text': '© 2026 IAbits Studio. Todos los derechos reservados.',
    'social_title': 'Síguenos en Instagram',
    'new_tab_label': '(se abre en una pestaña nueva)',
}

# Cuentas de Instagram del footer (home y /contacto/), en este orden.
# 'organization': True marca la cuenta oficial de la empresa: es la única que
# se publica en los datos estructurados (sameAs) como perfil de IAbits.
SOCIAL_LINKS = [
    {
        'name': 'IAbits Studio',
        'handle': '@iabits.studio',
        'url': 'https://www.instagram.com/iabits.studio/',
        'organization': True,
    },
    {
        'name': 'David Hernández',
        'handle': '@davidh.421',
        'url': 'https://www.instagram.com/davidh.421/',
        'organization': False,
    },
]

# Degradado oficial del logo de Instagram (colores de su guía de marca, no
# del tema): de amarillo, abajo a la izquierda, a violeta, arriba a la derecha.
INSTAGRAM_GRADIENT = [
    ('0', '#ffd600'),
    ('0.25', '#ff7a00'),
    ('0.5', '#ff0069'),
    ('0.75', '#d300c5'),
    ('1', '#7638fa'),
]

# Página de contacto (/contacto/): a ella llevan los botones de PRODUCTS y el
# de SUPPORT_SECTION. SEO con las mismas reglas que SITE y distinto del de la
# home y la landing; el <title> es fijo aunque el <h1> cambie según el botón.
CONTACT_SITE = {
    'name': BRAND['name'],
    'title': 'Contacto: diagnóstico e implementación | IAbits Studio',
    'meta_description': (
        'Solicita tu diagnóstico o la implementación de automatizaciones con IA '
        'para tu pyme. Te respondemos en menos de 24 horas y sin compromiso.'
    ),
}

# El <h1> no está aquí: sale de 'contact_heading' de lo que se solicita
# (PRODUCTS o INFO_REQUEST).
CONTACT_FORM = {
    'subtitle': (
        'Déjanos tus datos y te contactamos antes de 24 horas, '
        'sin ningún compromiso.'
    ),
    'submit_text': 'Enviar solicitud',
    'sending_text': 'Enviando…',
    'success_message': 'Gracias por tu solicitud. Te contactaremos en menos de 24 horas.',
    'error_message': (
        'No hemos podido enviar tu solicitud. Inténtalo de nuevo en unos minutos.'
    ),
    # Solo si alguien manipula el campo oculto del producto.
    'invalid_request': (
        'No hemos podido identificar qué solicitas. Vuelve a la página de inicio '
        'y pulsa de nuevo el botón.'
    ),
}

# Petición de información general: se solicita como un producto más, pero no
# es una tarjeta con precio (no está en PRODUCTS ni en el JSON-LD de ofertas).
# También es lo que se solicita al entrar en /contacto/ sin ?producto=.
INFO_REQUEST = {
    'slug': 'informacion',
    'name': 'Información',
    'contact_heading': 'Solicita información',
}

# (valor guardado en la BD, texto visible). El valor no puede pasar de 20
# caracteres: es el max_length de Lead.contact_preference.
CONTACT_PREFERENCES = [
    ('email', 'Email'),
    ('telefono', 'Teléfono'),
    ('videollamada', 'Videollamada'),
]


def contact_requests():
    """Lo que se puede solicitar en /contacto/: los productos y la información."""
    return [*PRODUCTS, INFO_REQUEST]


def get_contact_request(slug):
    """Lo que se solicita con ?producto=<slug>; INFO_REQUEST si no existe."""
    return next((r for r in contact_requests() if r['slug'] == slug), INFO_REQUEST)


def product_choices():
    """Choices para el campo 'producto' del formulario de contacto."""
    return [(r['slug'], r['name']) for r in contact_requests()]


def get_home_context():
    return {
        'site': SITE,
        'theme': THEME,
        'nav': NAV,
        'intro': INTRO,
        'products_section': PRODUCTS_SECTION,
        'products': PRODUCTS,
        'price_tax_note': PRICE_TAX_NOTE,
        'products_featured_label': PRODUCTS_FEATURED_LABEL,
        'support_featured_label': SUPPORT_FEATURED_LABEL,
        'support_section': SUPPORT_SECTION,
        'support_plans': SUPPORT_PLANS,
        'info_request': INFO_REQUEST,
        'tech_section': TECH_SECTION,
        'tech_items': TECH_ITEMS,
        'tech_partner': TECH_PARTNER,
        'team_section': TEAM_SECTION,
        'team': TEAM,
        'chat': CHAT,
        'contact': CONTACT,
        'footer': FOOTER,
        'social_links': SOCIAL_LINKS,
        'instagram_gradient': INSTAGRAM_GRADIENT,
    }


def get_contact_context():
    return {
        'site': CONTACT_SITE,
        'theme': THEME,
        'nav': NAV,
        'contact': CONTACT,
        'contact_form': CONTACT_FORM,
        'footer': FOOTER,
        'social_links': SOCIAL_LINKS,
        'instagram_gradient': INSTAGRAM_GRADIENT,
    }
