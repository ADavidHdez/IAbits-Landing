---
description: Añade un servicio nuevo a la landing y al formulario
argument-hint: [descripción del servicio]
---

Añade un servicio nuevo a la landing: **$ARGUMENTS**

Recuerda que `apps/landing/content.py` es la fuente única: añadir el servicio ahí
actualiza a la vez la sección de servicios de la web **y** el desplegable del
formulario, **sin migración** (los choices salen de `service_choices()`).

## Pasos

1. Lee `apps/landing/content.py` y fíjate en el estilo de los `Service` existentes:
   descripciones de dos líneas, orientadas al beneficio para el cliente, no a la
   tecnología. Tono directo, en español, tuteando.

2. Añade la entrada a la lista `SERVICES`:
   ```python
   Service(
       slug='...',        # kebab-case, sin acentos ni espacios — se guarda en el Lead
       icon='...',        # un emoji
       title='...',
       description='...',
   ),
   ```
   Colócalo en la posición que tenga sentido narrativo, no siempre al final.

3. Comprueba que **no** hace falta tocar nada más: ni `home.html` (itera sobre
   `services`), ni `main.css`, ni migraciones. Si crees que sí, párate y explica por qué
   antes de tocar nada.

4. Ejecuta `.venv/Scripts/python.exe manage.py test apps`. El test
   `test_renders_hero_and_services` recorre `content.SERVICES`, así que debería cubrir
   el nuevo automáticamente.

5. Resume: slug elegido, dónde lo colocaste y confirmación de que el formulario ya lo
   ofrece.

No toques el diseño ni el CSS.
