# Arquitectura

Cómo está montado el proyecto y **por qué** se tomó cada decisión. Si vas a cambiar
algo estructural, léelo antes: casi todo lo que parece raro tiene un motivo.

---

## Vista general

Una sola página pública (`/`) que hace dos cosas: vender y captar leads.
No hay registro de usuarios, ni área privada, ni API pública.

```
Visitante
   │  GET /
   ▼
LandingView (CreateView) ──► content.get_landing_context() ──► home.html
   │
   │  POST / (formulario)
   ▼
1. ¿honeypot relleno?  ──sí──► finge éxito, no guarda nada
2. ¿throttle por IP?   ──sí──► 429 / mensaje de error
3. LeadForm.is_valid() ──no──► reenvía errores (JSON o HTML)
4. Guarda el Lead en BD
5. transaction.on_commit ──► hilo daemon ──► POST JSON a n8n
6. Responde JSON (AJAX) o redirect a /#contacto (sin JS)
```

---

## Las dos apps

### `apps/landing`
Contiene todo lo relacionado con la página de ventas y la captación. Es donde vive
prácticamente el 100 % del trabajo.

### `apps/accounts`
Solo existe para tener un `User` propio (`AbstractUser` + campo `bio`) definido **antes**
de la primera migración — cambiar el modelo de usuario después es doloroso, así que se
hizo desde el principio aunque hoy apenas se use. Da login/logout para el admin.
No hay registro público a propósito: las únicas cuentas son de staff.

---

## Decisiones y su porqué

### `content.py` como fuente única de contenido
Todos los textos, los 5 servicios, los colores del tema y los datos de contacto viven en
un solo archivo Python. La plantilla solo los pinta.

**Por qué**: el dueño del proyecto puede cambiar cualquier copy o color editando un
archivo, sin tocar HTML, CSS ni base de datos, y sin riesgo de romper el diseño.

Consecuencia práctica: **nunca escribas texto literal en `home.html`**. Si necesitas una
frase nueva, añádela a `content.py` y referénciala desde la plantilla.

### Colores como variables CSS
`content.THEME` → bloque `<style>` con nonce en `home.html` → `:root { --color-primary: … }`
→ `main.css` los consume con `var(--color-primary, #1a56db)`.

El fallback del `var()` importa: si alguien borra una clave de `THEME`, la web sigue
viéndose bien en vez de quedarse en blanco.

### `UUIDField` como clave primaria de `Lead`
IDs no adivinables ni secuenciales. Evita que, si algún día un ID se expone, se pueda
deducir cuántos leads hay o enumerarlos.

### Servicios sin migración
`content.service_choices()` genera los `choices` del `<select>` en tiempo de ejecución
(en `LeadForm.__init__`, no como atributo de clase). `Lead.service_interest` es un
`CharField` libre, no un campo con `choices` fijos.

**Por qué**: añadir o renombrar un servicio no obliga a migrar la base de datos. El
coste es que un slug antiguo puede quedar huérfano — por eso el admin usa
`service_label()`, que cae al slug crudo si ya no existe en `SERVICES`.

### Tres capas contra el spam
1. **Honeypot** (`website`): campo oculto por CSS. Si viene relleno, la vista *finge
   éxito* en vez de dar error — así el bot no aprende cuál es el campo trampa.
2. **Throttle por IP respaldado en BD**: cuenta `Lead` por IP en una ventana temporal.
   Se hace contra la base de datos, no en memoria, **porque gunicorn corre 3 workers**
   y un contador en memoria sería inútil (cada worker tendría el suyo).
3. **CSRF** de Django, activo por defecto.

La IP sale de `X-Forwarded-For` (la añade el proxy de Easypanel). Es fiable solo porque
el puerto del contenedor no es alcanzable desde internet: la única entrada es el proxy.

### AJAX con degradación
`lead-form.js` intercepta el submit y envía por `fetch` con la cabecera
`X-Requested-With: XMLHttpRequest`. La vista detecta esa cabecera (`is_ajax`) y responde
JSON; si no está, mantiene el flujo clásico Post/Redirect/Get con mensajes de Django.

**Mantén siempre los dos caminos.** Si tocas `form_valid` / `form_invalid`, comprueba
que ambos siguen funcionando — hay tests para los dos.

### Webhook a n8n fuera del camino crítico
El lead se guarda primero y **siempre**; n8n solo recibe una copia. El envío ocurre:
- en `transaction.on_commit` — el hilo escribe `webhook_delivered_at` desde otra conexión,
  así que la fila debe estar ya confirmada o el `UPDATE` no encontraría nada;
- en un **hilo daemon** — el visitante no espera a que n8n responda;
- con todas las excepciones capturadas — un n8n caído no puede romper el formulario.

Si falla, queda registrado en el log y el lead aparece en el admin con la columna
*enviado a n8n* en rojo, reenviable con una acción.

Se usa `urllib` de la stdlib en lugar de `requests` para no añadir una dependencia.

### CSP estricta desde desarrollo
`SECURE_CSP` está en `base.py`, no en `production.py`, **a propósito**: así cualquier
recurso que la viole se detecta ya en local y no en producción.

Implicaciones al escribir código:
- Nada de `<script>` inline, `onclick=`, `style="…"` ni CDNs externos.
- El JS va en archivos bajo `static/js/` y se enlaza con `{% static %}`.
- El único inline permitido es el `<style>` del tema, que lleva nonce.

---

## Estructura de `home.html`

Secciones en orden, todas alimentadas por `content.py`:

| Sección | id | Fuente en `content.py` |
|---|---|---|
| Hero | — | `HERO` |
| Servicios (timeline con tarjetas 3D) | `#servicios` | `SERVICES_SECTION`, `SERVICES` |
| Propuestas de valor | — | `VALUE_PROPS_SECTION`, `VALUE_PROPS` |
| Cómo trabajamos | `#como-trabajamos` | `STEPS_SECTION`, `STEPS` |
| Social proof | — | **comentada** con `{% comment %}` |
| Contacto (formulario) | `#contacto` | `FORM_SECTION` |

Ojo: la sección "social proof" está comentada y hay un test
(`test_commented_out_sections_are_not_rendered`) que verifica que no se renderiza.
La sintaxis `{# … #}` solo comenta **una línea**; los bloques necesitan
`{% comment %}`.

---

## Atributos `data-*` que consume el JS

La plantilla y el JS se comunican por atributos `data-*`, nunca por clases CSS
(las clases son para estilo; así se puede reestilizar sin romper el comportamiento).

| Atributo | Lo usa | Para |
|---|---|---|
| `data-lead-form` | `lead-form.js` | Localizar el formulario |
| `data-field="<nombre>"` | `lead-form.js` | Colocar los errores de cada campo |
| `data-form-errors` / `data-form-feedback` | `lead-form.js` | Errores globales y mensaje de éxito |
| `data-sending-text` | `lead-form.js` | Texto del botón mientras envía |
| `data-reveal` / `data-reveal-group` | `reveal.js` | Animación de aparición al hacer scroll |
| `data-timeline` / `data-timeline-item` / `data-timeline-icon` | `timeline.js` | Línea temporal de servicios |
| `data-card-3d` | `cards-3d.js` | Inclinación 3D de las tarjetas |

Si renombras uno, busca el `.js` correspondiente antes.

---

## Tests

`apps/landing/tests/` — 47 tests. Cubren modelo, formulario, vista (GET, POST clásico,
POST AJAX), seguridad (CSRF, escapado XSS, admin protegido), throttle y webhook.

```bash
python manage.py test apps
```

Al probar el webhook se usa `self.captureOnCommitCallbacks(execute=True)`, porque los
callbacks de `on_commit` no se ejecutan dentro de un `TestCase` normal.
