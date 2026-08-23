# Despliegue

**GitHub → Easypanel (VPS) → Docker → gunicorn tras el proxy de Easypanel.**

---

## Checklist antes de desplegar

```bash
python manage.py test apps                 # 47 tests en verde
python manage.py makemigrations --check    # ¿falta alguna migración por generar?
python manage.py check --deploy            # avisos de seguridad de producción
git status                                 # nada sensible sin querer
```

Luego: commit → push a `origin/master` → Easypanel despliega (automático si tienes
auto-deploy; si no, botón **Deploy** en el panel).

> Existe el comando `/deploy-check` que ejecuta todo esto por ti.

---

## Qué pasa al arrancar el contenedor

El `CMD` del `Dockerfile` encadena, **en cada arranque**:

```
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy --fail-level ERROR
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 \
         --access-logfile - --error-logfile - --forwarded-allow-ips '*'
```

Consecuencias importantes:

- **Las migraciones se aplican solas.** No hace falta entrar a la consola del contenedor.
- **Un `check --deploy` en nivel ERROR impide arrancar.** Si tras un deploy el servicio
  no levanta, mira los logs: casi siempre es una variable de entorno que falta.
- `migrate` y `collectstatic` van en el arranque y no en el build porque necesitan las
  variables reales (`SECRET_KEY`, `DATABASE_URL`), que Easypanel solo inyecta en runtime.
- Corre como usuario `appuser` sin privilegios, no como root.

---

## Variables de entorno

En producción **no existe `.env`**: se configuran en Easypanel → tu servicio →
**Environment**. En local sí se usa `.env` (gitignored; `.env.example` es la plantilla).

### Obligatorias

| Variable | Notas |
|---|---|
| `SECRET_KEY` | Distinta de la de desarrollo. Generar con `get_random_secret_key()` |
| `DEBUG` | `False` en producción, siempre |
| `ALLOWED_HOSTS` | Separadas por comas, sin esquema |
| `DATABASE_URL` | `postgres://usuario:pass@servicio-db:5432/db` (host = nombre del servicio) |

### Recomendadas en producción

| Variable | Para qué |
|---|---|
| `CSRF_TRUSTED_ORIGINS` | Dominios **con** esquema desde los que se aceptan POST |
| `ADMIN_URL` | Ruta no adivinable del admin, terminada en `/` |
| `LEAD_THROTTLE_MAX` / `LEAD_THROTTLE_WINDOW_MINUTES` | Límite de envíos por IP |
| `N8N_WEBHOOK_URL` / `N8N_WEBHOOK_TOKEN` | Integración n8n (ver [integraciones.md](integraciones.md)) |

---

## Configuración por entorno

- `config/settings/base.py` — común. Aquí viven `SECURE_CSP` (a propósito, para detectar
  violaciones ya en local) y las variables de la app.
- `config/settings/development.py` — SQLite, `DEBUG=True`, email por consola,
  `WHITENOISE_AUTOREFRESH` para servir estáticos sin `collectstatic`.
- `config/settings/production.py` — Postgres vía `dj_database_url`, logging a stdout
  (Easypanel captura la consola), HSTS, cookies seguras, `SECURE_PROXY_SSL_HEADER`
  y storage de estáticos con manifest.

`manage.py` usa `development` por defecto; el `Dockerfile` fija `production` con
`DJANGO_SETTINGS_MODULE`.

---

## Trampas ya pisadas (no repetir)

- **Bucle de redirección HTTPS**: el proxy de Easypanel termina el TLS y habla con
  gunicorn por HTTP. Sin `SECURE_PROXY_SSL_HEADER`, Django cree que toda petición es
  insegura y redirige en bucle. Ya está configurado — no lo quites.
- **SSL con la base de datos**: Postgres vive en la red privada de Docker y no soporta
  SSL. `ssl_require` debe quedarse desactivado.
- **Puerto**: el proxy debe apuntar al **8000** interno, donde escucha gunicorn.
- **`collectstatic` y el manifest**: en producción se usa
  `CompressedManifestStaticFilesStorage`. Si referencias un estático que no existe, el
  arranque falla. En desarrollo no pasa porque se usa el storage simple.

---

## Base de datos

- Desarrollo: SQLite en `db.sqlite3` (gitignored).
- Producción: PostgreSQL como servicio aparte en Easypanel, `CONN_MAX_AGE=600` y
  health checks activados.

Las migraciones se commitean **junto al cambio de modelo** que las provoca.
