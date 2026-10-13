"""Textos legales de la web: aviso legal, privacidad y cookies.

Igual que los demás content.py, es la ÚNICA fuente de estos textos. Las páginas
legales son comunes a la home y a la landing, y las enlazan los pies de las dos
webs, el formulario de cada una y el aviso del chat.

Los datos del titular viven en OWNER y se reutilizan en los tres documentos. Si
cambia un proveedor, un plazo o lo que se guarda de cada visitante, hay que
actualizar PRIVACY (y COOKIES si afecta al navegador) y la fecha de UPDATED.

"""
from apps.landing.content import BRAND, CONTACT

UPDATED = '13 de octubre de 2026'

# Titular de la web (art. 10 de la LSSI-CE): autónomo, sin registro mercantil.
OWNER = {
    'name': 'Ángel David Hernández Marrero',
    'trade_name': BRAND['name'],
    'nif': '45981684S',
    # Solo el municipio, por decisión del titular: el art. 10 de la LSSI pide el
    # domicilio completo. Si se contrata una domiciliación, poner aquí esa dirección.
    'address': 'Granadilla de Abona (Santa Cruz de Tenerife)',
    'email': CONTACT['email'],
    'phone': '+34 644 510 220',
    'activity': (
        'servicios de automatización de procesos con inteligencia artificial, '
        'desarrollo de software a medida y diseño de páginas web'
    ),
}

# Plazos de conservación, en un solo sitio: los cita la política de privacidad.
RETENTION = {
    'leads': '3 meses desde el último contacto si no llegas a contratar',
    'chat': '6 meses desde el último mensaje',
    'clients': (
        'mientras dure la relación y, después, durante los plazos que exige la ley '
        '(hasta 6 años, por las obligaciones contables y fiscales)'
    ),
}


def p(text):
    """Párrafo de un documento legal. Las URL y los emails se enlazan solos."""
    return {'p': text}


def ul(*items):
    """Lista de un documento legal."""
    return {'ul': items}


def owner_items():
    return ul(
        f'Titular: {OWNER["name"]}, que opera con el nombre comercial {OWNER["trade_name"]}.',
        f'NIF: {OWNER["nif"]}.',
        f'Domicilio: {OWNER["address"]}.',
        f'Email: {OWNER["email"]}.',
        f'Teléfono: {OWNER["phone"]}.',
    )


LEGAL_NOTICE = {
    'slug': 'aviso-legal',
    'heading': 'Aviso legal',
    'site': {
        'name': BRAND['name'],
        'title': f'Aviso legal | {BRAND["name"]}',
        'meta_description': (
            f'Aviso legal de {BRAND["name"]}: datos del titular de la web, '
            'condiciones de uso, precios y propiedad intelectual.'
        ),
    },
    'sections': [
        {
            'title': 'Datos del titular',
            'body': [
                p(
                    'En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de '
                    'la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), '
                    'te informamos de quién está detrás de este sitio web:'
                ),
                owner_items(),
                p(f'Actividad: {OWNER["activity"]}.'),
            ],
        },
        {
            'title': 'Objeto y condiciones de uso',
            'body': [
                p(
                    f'Este sitio web da a conocer los servicios de {OWNER["trade_name"]} y '
                    'permite solicitar información o un presupuesto. Navegar por él '
                    'implica aceptar este aviso legal.'
                ),
                p(
                    'Te comprometes a usar la web de forma lícita y a no enviar a través '
                    'de sus formularios o del chat contenidos falsos, ilícitos, ofensivos '
                    'o que puedan dañar el sitio o a terceros.'
                ),
            ],
        },
        {
            'title': 'Precios',
            'body': [
                p(
                    'Los precios publicados son los vigentes en cada momento, incluyen los '
                    'impuestos indirectos aplicables y pueden cambiar sin previo aviso. '
                    'El precio que se aplica a cada encargo es el del presupuesto que '
                    'aceptes antes de empezar el trabajo.'
                ),
            ],
        },
        {
            'title': 'Asistente de inteligencia artificial',
            'body': [
                p(
                    'El chat de la web lo atiende un asistente de inteligencia artificial, '
                    'no una persona. Sus respuestas se generan automáticamente, son '
                    'orientativas y pueden contener errores: no constituyen una oferta '
                    'vinculante ni asesoramiento profesional. Las condiciones válidas son '
                    'las que te confirmemos por escrito.'
                ),
            ],
        },
        {
            'title': 'Propiedad intelectual e industrial',
            'body': [
                p(
                    f'Los textos, el diseño, el logotipo y el código de esta web pertenecen '
                    f'a {OWNER["name"]} o se usan con permiso de sus titulares. No está '
                    'permitido copiarlos, distribuirlos ni modificarlos sin autorización '
                    'expresa.'
                ),
                p(
                    'Las marcas y logotipos de terceros que aparecen en la web pertenecen '
                    'a sus respectivos titulares y se muestran solo con fines informativos.'
                ),
            ],
        },
        {
            'title': 'Enlaces y responsabilidad',
            'body': [
                p(
                    'La web enlaza a sitios de terceros, como Instagram. No controlamos su '
                    'contenido ni respondemos de él; al visitarlos se aplican sus propias '
                    'condiciones y políticas.'
                ),
                p(
                    'Procuramos que la web funcione sin interrupciones y que su información '
                    'sea correcta, pero no podemos garantizarlo en todo momento ni '
                    'respondemos de los daños que pudieran derivarse de una interrupción '
                    'ajena a nuestra voluntad.'
                ),
            ],
        },
        {
            'title': 'Protección de datos',
            'body': [
                p(
                    'El tratamiento de tus datos personales se explica en la política de '
                    'privacidad, y el uso de cookies en la política de cookies, ambas '
                    'enlazadas al pie de cada página.'
                ),
            ],
        },
        {
            'title': 'Legislación y jurisdicción',
            'body': [
                p(
                    'Este aviso legal se rige por la ley española. Si eres consumidor, '
                    'cualquier conflicto se resolverá en los juzgados de tu domicilio; en '
                    'los demás casos, en los del domicilio del titular.'
                ),
            ],
        },
    ],
}

PRIVACY = {
    'slug': 'privacidad',
    'heading': 'Política de privacidad',
    'site': {
        'name': BRAND['name'],
        'title': f'Política de privacidad | {BRAND["name"]}',
        'meta_description': (
            f'Cómo trata {BRAND["name"]} los datos de sus formularios y de su chat: '
            'finalidades, plazos, proveedores y cómo ejercer tus derechos.'
        ),
    },
    'sections': [
        {
            'title': 'Responsable del tratamiento',
            'body': [
                owner_items(),
                p(
                    'Dentro de nuestra organización, solo el titular accede a los datos que '
                    'nos facilitas. No contamos con '
                    'delegado de protección de datos porque nuestra actividad no lo exige; '
                    'para cualquier cuestión sobre tus datos, escríbenos al email anterior.'
                ),
            ],
        },
        {
            'title': 'Qué datos tratamos',
            'body': [
                ul(
                    'Formularios de contacto: nombre, email, teléfono y empresa (estos dos '
                    'últimos, opcionales), el servicio o plan que te interesa, cómo '
                    'prefieres que te contactemos y tu mensaje.',
                    'Chat: los mensajes que escribas al asistente y la fecha de cada uno. '
                    'El chat no te pide datos personales; te pedimos que no incluyas datos '
                    'sensibles (de salud, bancarios, etc.).',
                    'Datos técnicos: la dirección IP y el navegador desde los que envías '
                    'un formulario o un mensaje del chat. Tu IP también puede quedar en '
                    'los registros de actividad del servidor.',
                    'Si llegas a ser cliente: los datos necesarios para prestar el servicio '
                    'y facturarlo.',
                ),
            ],
        },
        {
            'title': 'Para qué los usamos y con qué legitimación',
            'body': [
                ul(
                    'Responder a tu solicitud de información, diagnóstico o presupuesto y '
                    'hablar contigo sobre ella. Base jurídica: la aplicación de medidas '
                    'precontractuales a petición tuya (art. 6.1.b del RGPD).',
                    'Contestar a tus preguntas en el chat mediante un asistente de '
                    'inteligencia artificial. Base jurídica: tu propia petición de '
                    'información previa a una posible contratación (art. 6.1.b del RGPD).',
                    'Proteger la web frente al spam y los abusos, limitando los envíos por '
                    'dirección IP. Base jurídica: nuestro interés legítimo en mantener el '
                    'servicio seguro (art. 6.1.f del RGPD).',
                    'Prestar y facturar los servicios contratados. Base jurídica: la '
                    'ejecución del contrato y el cumplimiento de obligaciones legales '
                    '(art. 6.1.b y 6.1.c del RGPD).',
                ),
                p(
                    'No te enviaremos publicidad ni boletines, no elaboramos perfiles y no '
                    'tomamos decisiones automatizadas que te afecten: el asistente del chat '
                    'solo responde preguntas.'
                ),
            ],
        },
        {
            'title': 'Cuánto tiempo los conservamos',
            'body': [
                ul(
                    f'Solicitudes de los formularios: {RETENTION["leads"]}.',
                    f'Conversaciones del chat: {RETENTION["chat"]}.',
                    f'Datos de clientes: {RETENTION["clients"]}.',
                ),
                p(
                    'Los datos técnicos se conservan el mismo tiempo que la solicitud o la '
                    'conversación a la que acompañan, y los registros del servidor se '
                    'renuevan periódicamente. Pasados estos plazos, los borramos.'
                ),
            ],
        },
        {
            'title': 'Quién más trata tus datos',
            'body': [
                p(
                    'No cedemos tus datos a nadie, salvo obligación legal (por ejemplo, a la '
                    'Administración tributaria). Para funcionar, la web se apoya en estos '
                    'proveedores, que tratan los datos solo por cuenta nuestra y bajo '
                    'contrato:'
                ),
                ul(
                    'Hostinger: alojamiento de la web, de su base de datos y de las '
                    'herramientas que automatizan la gestión de solicitudes, en un servidor '
                    'situado en Fráncfort (Alemania), y correo electrónico con el que '
                    'respondemos a tus solicitudes.',
                    'Airtable (Estados Unidos): gestión de las solicitudes de contacto.',
                    'OpenRouter (Estados Unidos): plataforma que envía los mensajes del '
                    'chat al modelo de inteligencia artificial que genera las respuestas, '
                    'de proveedores como Anthropic, OpenAI o Google. Reciben solo los '
                    'mensajes de la conversación, no los datos de los formularios.',
                ),
            ],
        },
        {
            'title': 'Transferencias internacionales',
            'body': [
                p(
                    'Airtable, OpenRouter y los proveedores de modelos de inteligencia '
                    'artificial pueden tratar datos fuera del Espacio Económico Europeo, '
                    'principalmente en Estados Unidos. '
                    'Estas transferencias se amparan en el Marco de Privacidad de Datos '
                    'UE-EE. UU., cuando el proveedor está adherido a él, o en las cláusulas '
                    'contractuales tipo aprobadas por la Comisión Europea, que garantizan '
                    'un nivel de protección equivalente al europeo.'
                ),
            ],
        },
        {
            'title': 'Tus derechos',
            'body': [
                p(
                    'Puedes pedirnos en cualquier momento acceder a tus datos, '
                    'rectificarlos o suprimirlos, oponerte a su tratamiento, limitarlo o '
                    'recibirlos en un formato portable. Escríbenos a '
                    f'{OWNER["email"]} indicando qué derecho quieres ejercer; te '
                    'responderemos en el plazo máximo de un mes.'
                ),
                p(
                    'Si crees que no hemos tratado bien tus datos, puedes presentar una '
                    'reclamación ante la Agencia Española de Protección de Datos '
                    '(https://www.aepd.es), aunque te agradeceremos que antes nos lo '
                    'cuentes para intentar resolverlo.'
                ),
            ],
        },
        {
            'title': 'Seguridad y otras cuestiones',
            'body': [
                p(
                    'La web funciona con conexión cifrada (HTTPS) y aplicamos medidas '
                    'técnicas y organizativas para proteger tus datos frente a accesos no '
                    'autorizados, pérdidas o alteraciones.'
                ),
                p(
                    'Nuestros servicios se dirigen a empresas y profesionales: no '
                    'recogemos conscientemente datos de menores de 14 años. Si nos das '
                    'datos de otra persona, debes haberla informado antes.'
                ),
                p(
                    'Podemos actualizar esta política para adaptarla a cambios legales o '
                    'en nuestros servicios; la fecha de la última versión figura arriba.'
                ),
            ],
        },
    ],
}

COOKIES = {
    'slug': 'cookies',
    'heading': 'Política de cookies',
    'site': {
        'name': BRAND['name'],
        'title': f'Política de cookies | {BRAND["name"]}',
        'meta_description': (
            f'{BRAND["name"]} solo usa cookies técnicas, imprescindibles para que la '
            'web funcione: sin analítica ni publicidad. Consulta cuáles y para qué.'
        ),
    },
    'sections': [
        {
            'title': 'Qué son las cookies',
            'body': [
                p(
                    'Las cookies son pequeños archivos que una web guarda en tu navegador '
                    'para recordar información entre una página y otra. Hay tecnologías '
                    'parecidas, como el almacenamiento de sesión del navegador, a las que '
                    'se aplican las mismas reglas.'
                ),
            ],
        },
        {
            'title': 'Qué cookies usa esta web',
            'body': [
                p(
                    'Solo usamos cookies propias y técnicas, imprescindibles para que la web '
                    'funcione. No usamos cookies de analítica, de publicidad ni de terceros.'
                ),
                ul(
                    'csrftoken: protege los formularios y el chat frente a envíos '
                    'falsificados desde otras webs. Caduca al año.',
                    'messages: muestra el mensaje de confirmación tras enviar un formulario '
                    'cuando el navegador no ejecuta JavaScript. Se borra al mostrarse.',
                    'sessionid: mantiene abierta la sesión del administrador de la web. Los '
                    'visitantes no la reciben.',
                ),
                p('Además, el chat guarda en el almacenamiento de sesión de tu navegador:'),
                ul(
                    'iabits-chat-conversation: el identificador de tu conversación, para '
                    'que no se pierda al cambiar de página.',
                    'iabits-chat-seen e iabits-chat-teaser: si ya abriste el chat o viste '
                    'el aviso de bienvenida, para no repetírtelo.',
                ),
                p('Estos datos se borran solos al cerrar la pestaña.'),
            ],
        },
        {
            'title': 'Consentimiento',
            'body': [
                p(
                    'Las cookies técnicas están exentas de consentimiento según el artículo '
                    '22.2 de la LSSI-CE, por eso no te mostramos ningún aviso para '
                    'aceptarlas. Si algún día añadimos cookies que no sean técnicas, te '
                    'pediremos permiso antes de usarlas.'
                ),
            ],
        },
        {
            'title': 'Cómo desactivarlas',
            'body': [
                p(
                    'Puedes bloquear o borrar las cookies desde la configuración de tu '
                    'navegador. Ten en cuenta que, sin ellas, los formularios y el chat '
                    'dejarán de funcionar.'
                ),
                p(
                    'Los enlaces a Instagram del pie de página no instalan nada mientras '
                    'no los pulses; al hacerlo, se aplica la política de cookies de '
                    'Instagram.'
                ),
            ],
        },
    ],
}

PAGES = [LEGAL_NOTICE, PRIVACY, COOKIES]

# Enlaces del pie (home, contacto, landing y las propias páginas legales), en
# este orden. 'url_name' es el nombre de la ruta en apps/legal/urls.py.
FOOTER_LINKS = [
    {'url_name': 'legal:notice', 'text': 'Aviso legal'},
    {'url_name': 'legal:privacy', 'text': 'Privacidad'},
    {'url_name': 'legal:cookies', 'text': 'Cookies'},
]

FOOTER_LINKS_LABEL = 'Información legal'

UPDATED_LABEL = 'Última actualización'

# Casilla obligatoria de los formularios de leads (landing y /contacto/): el
# enlace va entre 'before' y 'after'. 'notice' es la información básica que
# exige el art. 11 de la LOPDGDD junto al formulario.
FORM_CONSENT = {
    'before': 'He leído y acepto la ',
    'link_text': 'política de privacidad',
    'after': '.',
    'new_tab_label': '(se abre en una pestaña nueva)',
    'required_message': 'Debes aceptar la política de privacidad para enviar el formulario.',
    'notice': (
        f'Responsable: {OWNER["name"]}. Usaremos tus datos solo para responder a tu '
        'solicitud y no los cederemos a terceros. Puedes acceder a ellos, '
        'rectificarlos o suprimirlos, entre otros derechos, como se explica en la '
        'política.'
    ),
}
