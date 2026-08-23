---
description: Añade una sección nueva a la landing siguiendo el patrón del proyecto
argument-hint: [qué sección y qué debe contener]
---

Añade una sección nueva a la landing: **$ARGUMENTS**

Sigue el patrón del proyecto en este orden exacto. Lee antes
`docs/contenido-y-estilo.md` si necesitas el detalle.

## 1. `apps/landing/content.py`

Define los textos siguiendo el estilo de las secciones existentes: un diccionario
`XXX_SECTION` con `title` y (si procede) `subtitle`, más la lista de elementos.
Todo el copy va aquí — **nada de texto literal en la plantilla**.

## 2. `content.get_landing_context()`

Añade las claves nuevas al diccionario que devuelve, o la plantilla no las verá.

## 3. `apps/landing/templates/landing/home.html`

Inserta el `<section>` en el punto que corresponda al recorrido de venta (hero →
servicios → propuestas de valor → cómo trabajamos → contacto).

- Reutiliza clases existentes: `section-sub`, `card`, `btn`, `props-grid`, `steps-grid`.
- Añade `data-reveal` (o `data-reveal-group` en el contenedor) para que herede la
  animación de aparición al hacer scroll.
- Solo variables de contexto, cero literales.

## 4. `static/css/main.css`

**Solo si hace falta un estilo que no exista ya.** Usa `var(--color-…, #fallback)`,
nunca colores literales. Si puedes resolverlo reutilizando clases, mejor: no añadas CSS.

## 5. Test

Añade en `apps/landing/tests/test_views.py` una comprobación de que el contenido nuevo
se renderiza, comparando contra `content.*` (nunca contra un literal copiado), al estilo
de `test_renders_hero_and_services`.

Ejecuta `.venv/Scripts/python.exe manage.py test apps`.

## Al terminar

Di qué archivos tocaste y confirma que el resto del diseño quedó intacto.
