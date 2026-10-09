"""Configuración de contenido de la web home.

Este archivo es la ÚNICA fuente de textos de la home, igual que
apps/landing/content.py lo es de la landing. Los colores y el contacto se
comparten con la landing para que las dos webs se vean como una sola marca.

Los valores marcados con «PROVISIONAL» son de relleno: hay que sustituirlos
por los reales antes de publicar.
"""
from apps.landing.content import BRAND, CONTACT, THEME

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
}

# Bloque 1: presentación del negocio.
INTRO = {
    'eyebrow': 'Automatización con IA',
    'headline': 'Automatización con IA para llevar tu negocio al siguiente nivel.',
    'description': (
            'La Inteligencia Artificial no es el futuro, ya es el presente.\n'
            'Sin embargo, muchos negocios continúan sin dar el paso.\n\n'
            'En IAbits nos preocupamos por tu negocio. Nosotros nos encargamos de detectar los cuellos de botella. '
            'Estudiamos cómo optimizarlo, lo implementamos y te enseñamos a usarlo.'
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
    'title': 'Nuestros servicios',
    'subtitle': 'Empieza por saber dónde ganar tiempo y, después, lo hacemos realidad.',
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
            'Mapa de tus procesos actuales siguiendo el Estándar ISO 9001:2015',
            'Lista priorizada de automatizaciones',
            'Estimación de horas y dinero ahorrados',
            'Informe final con hoja de ruta',
        ],
        'cta_text': 'Solicitar diagnóstico',
        # <h1> de /contacto/ cuando se llega desde este botón.
        'contact_heading': 'Solicita tu diagnóstico',
        'featured': False,
    },
    {
        'slug': 'implementacion',
        'name': 'Implementación',
        'summary': 'Ponemos en marcha la automatización y la dejamos funcionando.',
        'price': 'desde 700 €',  # PROVISIONAL
        'price_note': 'según alcance',  # PROVISIONAL
        'features': [  # PROVISIONAL
            'Todo lo incluido en el Diagnóstico',
            'Desarrollo e integración con tus herramientas',
            'Agentes de IA y flujos automáticos a medida',
            'Formación para tu equipo',
            '30 días de soporte tras la entrega',
            'Se descontará el precio del Diagnóstico'
        ],
        'cta_text': 'Solicitar implementación',
        'contact_heading': 'Solicita tu implementación',
        'featured': True,
    },
]

PRODUCTS_FEATURED_LABEL = 'El más completo'

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
            'price': '59 €',  # PROVISIONAL
            'price_note': 'según alcance',  # PROVISIONAL
            'features': [  # PROVISIONAL
                'Mantenimiento de tus automatizaciones base',
                'Actualizaciones de tus agentes de IA',
            ],
            'cta_text': '',
            'featured': False,
        },
    
    {
        'slug': 'premium', 
        'name': 'Premium', 
        'summary': 'Lo ideal para mantener tus automatizaciones sin preocupaciones', 
        'price': '99 €',
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
        'name': 'Advanced', 
        'summary': 'La opción más completa para mantener tus automatizaciones al día', 
        'price': '159 €', 
        'price_note': 
        '/ mes', 
        'features': [
            'Mantenimiento de tus automatizaciones Plus',
            'Actualizaciones de tus agentes de IA',
            'Revisiones de seguridad y optimizaciones periódicas',
            'Soporte prioritario 24/7',
            'Mejoras y nuevas implementaciones según tus necesidades'
        ], 
        'cta_text': '', 
        'featured':False
    },
]

# Bloque 4: la tecnología con la que trabajamos.
TECH_SECTION = {
    'title': 'Nuestra tecnología',
    'subtitle': 'Potenciados por la tecnología de',
}

# Marca que acompaña al subtítulo, enlazada a su web. La CSP solo admite
# imágenes propias: el logo va en static/img/, nunca enlazado desde otra web.
# Es solo el emblema recortado del póster original, ya en círculo con las
# esquinas transparentes, y se pinta junto al nombre. Sin 'logo' queda solo el nombre, y sin 'url' la marca
# aparece sin enlace.
TECH_PARTNER = {
    'name': 'IA ORION',
    'url': 'https://iaorion.com/',
    'logo': 'img/iaorion.webp',
    'new_tab_label': '(se abre en una pestaña nueva)',
}

TECH_ITEMS = [  # PROVISIONAL
    {
        'name': 'Agentes de IA',
        'text': (
            'Asistentes que atienden a tus clientes, responden dudas y '
            'ejecutan tareas por ti, a cualquier hora.'
        ),
    },
    {
        'name': 'Automatización de flujos',
        'text': (
            'Conectamos tus herramientas para que los datos y las tareas '
            'repetitivas se muevan solos, sin copiar y pegar.'
        ),
    },
    {
        'name': 'Bases de conocimiento',
        'text': (
            'La información de tu empresa ordenada y consultable con IA, '
            'para que tu equipo encuentre respuestas en segundos.'
        ),
    },
    {
        'name': 'Integraciones Inteligentes',
        'text': (
            'Enlazamos la IA con tu correo, tu CRM, tu web y el resto de los '
            'sistemas que ya usas para que trabajen juntos y sin errores.'
        ),
    },
    {
        'name': 'Software a medida',
        'text': (
            'Herramientas a medida para tareas específicas de tu negocio potenciadas con IA e '
            'integradas con sistemas que ya usas.'
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
            'Diseño e implemento automatizaciones con inteligencia artificial '
            'para pequeñas y medianas empresas. Yo junto a mi equipo nos encargamos de ofrecer el mejor resultado posible. '
            'Vamos de principio a fin, entendiendo cómo trabajas, pensando la solución con '
            'más retorno y nos aseguramos de que funcione en el día a día.'
        ),
        'photo': '',  # Igual que INTRO['photo']: ruta dentro de static/.
        'photo_placeholder': 'Foto próximamente',
    },
]

FOOTER = {
    'text': '© 2026 IAbits Studio. Todos los derechos reservados.',
}

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
        'products_featured_label': PRODUCTS_FEATURED_LABEL,
        'support_section': SUPPORT_SECTION,
        'support_plans': SUPPORT_PLANS,
        'info_request': INFO_REQUEST,
        'tech_section': TECH_SECTION,
        'tech_items': TECH_ITEMS,
        'tech_partner': TECH_PARTNER,
        'team_section': TEAM_SECTION,
        'team': TEAM,
        'contact': CONTACT,
        'footer': FOOTER,
    }


def get_contact_context():
    return {
        'site': CONTACT_SITE,
        'theme': THEME,
        'nav': NAV,
        'contact': CONTACT,
        'contact_form': CONTACT_FORM,
        'footer': FOOTER,
    }
