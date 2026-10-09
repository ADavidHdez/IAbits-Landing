# IAbits Studio — Web

Web de **IAbits Studio**, agencia de automatización con IA, publicada en
<https://iabits.tech>. Tiene dos páginas sin enlaces entre ellas:

- **`/`** — home de presentación de la empresa (productos, planes de soporte, equipo).
- **`/landing/`** — landing de captación: el formulario guarda el lead en base de datos
  y lo reenvía a n8n por webhook. Incluye un chat opcional con un agente de IA.

**Django 6 · Python 3.13 · SQLite (dev) / PostgreSQL (prod) · Docker + Easypanel**

> Todo lo de cara al usuario —contenido, comentarios, commits— está en español.

---

## Arranque en local

```bash
python -m venv .venv
.venv\Scripts\activate                  # Linux/Mac: source .venv/bin/activate
pip install -r requirements/development.txt

copy .env.example .env                  # Linux/Mac: cp .env.example .env
#  y edita SECRET_KEY dentro de .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La web queda en <http://127.0.0.1:8000/> y el admin en <http://127.0.0.1:8000/admin/>.

## Comandos del día a día

```bash
python manage.py runserver          # servidor de desarrollo
python manage.py test apps          # suite completa
python manage.py makemigrations landing
python manage.py check --deploy     # antes de desplegar
```

---

## Mapa del proyecto

```
apps/
  landing/     La landing: captación de leads y chat con el agente de IA
    content.py   Textos de la landing + marca, tema y contacto (compartidos)
    views.py     LandingView (honeypot, throttle, AJAX/JSON) y ChatView
    webhooks.py  Envío del lead a n8n, en un hilo aparte
    chat.py      Llamada síncrona al agente de IA de n8n
  home/        La home de presentación (sin modelos)
    content.py   Textos de la home
  accounts/    User propio + login de staff con límite de intentos
  common/      Utilidades compartidas: IP del visitante y SEO (robots, sitemap, JSON-LD)
config/        Configuración: settings/{base,development,production}.py, urls, wsgi
templates/     base.html y parciales
static/        css/main.css, js/*.js, img/
docs/          Documentación por temas (ver tabla abajo)
n8n/           Workflows importables en n8n (webhook de leads y agente del chat)
requirements/  base.txt + development.txt + production.txt
```

**URLs**: `/` → home · `/landing/` → landing · `/landing/chat/` → chat (POST JSON) ·
`/accounts/login/` → acceso de staff · `/robots.txt` · `/sitemap.xml` · admin en
`ADMIN_URL` (ruta secreta en producción).

---

## Cuatro reglas que conviene conocer antes de tocar nada

1. **Los `content.py` son la única fuente de contenido.** `apps/landing/content.py`
   tiene la marca, el tema y el contacto compartidos; `apps/home/content.py`, los textos
   de la home. Nunca escribas texto literal en una plantilla ni un color en el CSS.
2. **CSP estricta** (`SECURE_CSP` en `config/settings/base.py`): prohibido JS inline,
   `onclick=`, CSS inline y recursos externos (CDN, Google Fonts). El único inline
   permitido es el `<style>` del tema, que va con nonce.
3. **Nada de secretos en el repo.** Todo por variables de entorno vía `python-decouple`;
   la plantilla de referencia es `.env.example`.
4. **Tests con cada cambio de lógica**: `python manage.py test apps`.

---

## Documentación

| Archivo | Cuándo abrirlo |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Flujo completo de una petición, decisiones de diseño y su porqué |
| [docs/contenido-y-estilo.md](docs/contenido-y-estilo.md) | Editar textos, colores, secciones o animaciones |
| [docs/integraciones.md](docs/integraciones.md) | Webhook n8n: payload, variables, Airtable/Telegram · chat con el agente de IA |
| [docs/despliegue.md](docs/despliegue.md) | Easypanel, Docker, variables de entorno, checklist de deploy |
| [docs/convenciones.md](docs/convenciones.md) | Estilo de código y patrones Django aplicables aquí |

`CLAUDE.md` es la versión condensada de todo esto para agentes de IA.
