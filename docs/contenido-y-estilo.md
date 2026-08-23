# Contenido y estilo

Cómo cambiar lo que se ve en la web sin romper nada.

> **Regla previa**: si la tarea es de backend, **no toques nada de este documento**.
> El diseño solo se modifica cuando se pide de forma explícita.

---

## Cambiar un texto

Todo el copy está en `apps/landing/content.py`. Busca el diccionario de la sección y
edita el valor. No hace falta tocar plantillas, ni CSS, ni migrar.

| Quiero cambiar… | Edita |
|---|---|
| Título/subtítulo/botón del hero | `HERO` |
| Nombre del sitio, tagline, meta description | `SITE` |
| Título y subtítulo de la sección de servicios | `SERVICES_SECTION` |
| Los servicios en sí | `SERVICES` (lista de `Service`) |
| Bloques "por qué automatizar" | `VALUE_PROPS_SECTION`, `VALUE_PROPS` |
| Pasos "cómo trabajamos" | `STEPS_SECTION`, `STEPS` |
| Textos del formulario y mensajes de éxito/error | `FORM_SECTION` |
| Email y teléfono | `CONTACT` |
| Pie de página | `FOOTER` |

**Nunca** escribas la frase directamente en `home.html`: rompe la regla de fuente única
y hace que el dueño del proyecto ya no pueda cambiarla solo.

Si un test comprueba ese texto (varios lo hacen, comparando contra `content.*`),
seguirá pasando automáticamente porque lee del mismo sitio.

---

## Añadir o quitar un servicio

Edita la lista `SERVICES` en `content.py`:

```python
Service(
    slug='nuevo-servicio',       # sin acentos ni espacios; se guarda en el Lead
    icon='🚀',                    # emoji, va tal cual al HTML
    title='Título del servicio',
    description='Dos líneas explicando el beneficio, no la tecnología.',
),
```

Eso actualiza a la vez la sección de servicios de la web **y** el desplegable del
formulario (vía `service_choices()`), sin migración.

Si quitas un servicio, los leads antiguos conservarán su slug: el admin lo mostrará
crudo en vez del título, que es el comportamiento esperado.

---

## Cambiar colores o el aspecto global

Edita el diccionario `THEME` en `content.py`:

```python
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
```

Recorrido: `THEME` → bloque `<style>` con nonce en `home.html` → `:root { --color-… }`
→ `main.css` con `var(--color-primary, #1a56db)`.

Si añades una clave nueva a `THEME`, hay que declararla también en el bloque `<style>`
de `home.html` para que llegue al CSS. Y en `main.css` úsala **siempre con fallback**:
`var(--mi-color, #valor)`.

---

## Añadir una sección nueva a la landing

Cuatro pasos, en este orden:

1. **`content.py`**: define el diccionario o la lista con los textos, siguiendo el patrón
   de las secciones existentes (`XXX_SECTION` con `title`/`subtitle`, más los datos).
2. **`content.get_landing_context()`**: añade la clave al diccionario que devuelve, o la
   plantilla no la verá.
3. **`home.html`**: añade el `<section>` en el punto que corresponda, referenciando solo
   variables de contexto. Reutiliza clases existentes (`section-sub`, `card`, `btn`…) y
   `data-reveal` para que herede la animación de scroll.
4. **`main.css`**: solo si necesitas estilos que no existan. Usa `var(--…)`, nunca
   colores literales.

Añade un test en `apps/landing/tests/test_views.py` que compruebe que el título nuevo
se renderiza, siguiendo el estilo de `test_renders_hero_and_services`.

---

## Las animaciones

Cinco scripts independientes en `static/js/`, todos sin dependencias externas
(la CSP prohíbe CDNs):

| Archivo | Qué hace |
|---|---|
| `reveal.js` | Aparición progresiva al hacer scroll (`data-reveal`) |
| `timeline.js` | Línea temporal que dibuja los servicios (`data-timeline`) |
| `cards-3d.js` | Inclinación 3D de tarjetas al pasar el ratón (`data-card-3d`) |
| `confetti.js` | Expone `window.launchConfetti`, usado al enviar el formulario |
| `lead-form.js` | Envío AJAX del formulario (no es animación, pero convive con ellas) |

Se activan por atributos `data-*`, no por clases. Puedes reestilizar libremente sin
romper el comportamiento, siempre que conserves esos atributos.

Todos comprueban que el elemento existe antes de actuar, así que una sección puede
quitarse sin que el JS falle.

---

## El logo

`static/img/logo-trimmed.png` es `logo.png` recortado: el original tenía un margen
transparente que ocupaba el 63 % del alto del archivo, lo que hacía que el logo se viera
diminuto dentro de su caja.

**Si sustituyes el logo, recorta el nuevo igual** (sin margen transparente) o se verá
desproporcionado. El destello luminoso lo aporta el pseudo-elemento de `.logo-frame`,
no la imagen — por eso el `<img>` va envuelto en un `<span>`.

---

## Comprobar que no rompiste el diseño

```bash
python manage.py test apps        # los tests de render verifican textos y tema
python manage.py runserver        # y míralo en el navegador
```

Revisa también la consola del navegador: un error de CSP aparece ahí y significa que
metiste algo inline o externo que la política bloquea.
