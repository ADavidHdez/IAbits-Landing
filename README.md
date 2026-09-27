# IAbits Studio — Landing

Landing de una sola página para **IAbits Studio**, agencia de automatización con IA.
Capta leads por formulario, los guarda en base de datos y los reenvía a n8n por webhook.

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
python manage.py test apps          # suite completa (67 tests)
python manage.py makemigrations landing
python manage.py check --deploy     # antes de desplegar
```

---

## Mapa del proyecto

```
apps/
  landing/     La landing y la captación de leads. Aquí está casi todo el trabajo.
    content.py   ÚNICA fuente de textos, colores, servicios y datos de contacto
    views.py     LandingView: honeypot, throttle, respuesta AJAX/JSON
    webhooks.py  Envío del lead a n8n, en un hilo aparte
  accounts/    User propio + login de staff con límite de intentos
  common/      Utilidades compartidas (no es una app de Django)
config/        Configuración: settings/{base,development,production}.py, urls, wsgi
templates/     base.html y parciales
static/        css/main.css, js/*.js, img/
docs/          Documentación por temas (ver tabla abajo)
n8n/           Workflow importable en n8n
requirements/  base.txt + development.txt + production.txt
```

**URLs**: `/` → landing · `/accounts/login/` → acceso de staff · admin en `ADMIN_URL`
(ruta secreta en producción).

---

## Cuatro reglas que conviene conocer antes de tocar nada

1. **`apps/landing/content.py` es la única fuente de contenido.** Nunca escribas texto
   literal en una plantilla ni un color en el CSS: van ahí.
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
| [docs/integraciones.md](docs/integraciones.md) | Webhook n8n: payload, variables, Airtable/Telegram |
| [docs/despliegue.md](docs/despliegue.md) | Easypanel, Docker, variables de entorno, checklist de deploy |
| [docs/convenciones.md](docs/convenciones.md) | Estilo de código y patrones Django aplicables aquí |

`CLAUDE.md` es la versión condensada de todo esto para agentes de IA.
