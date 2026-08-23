---
name: copy-iabits
description: Escribe o revisa el copy comercial de la landing de IAbits Studio. Úsala siempre que haya que redactar, reescribir, acortar o mejorar textos de cara al visitante — titulares, subtítulos, descripciones de servicios, propuestas de valor, pasos, llamadas a la acción, textos del formulario o mensajes de éxito y error.
---

# Copy de IAbits Studio

IAbits Studio es una agencia de automatización con IA. El visitante típico es dueño o
responsable de una pyme: tiene poco tiempo, sospecha que pierde horas en tareas
repetitivas y desconfía de las promesas grandilocuentes sobre IA.

## Dónde va el copy

**Siempre en `apps/landing/content.py`**, nunca escrito directamente en la plantilla.
Consulta [docs/contenido-y-estilo.md](../../../docs/contenido-y-estilo.md) para saber qué
diccionario corresponde a cada sección.

## Voz

- **Español de España, tuteando.** Cercano pero profesional, nunca coloquial de más.
- **Frases cortas.** Si una frase necesita una coma para respirar dos veces, pártela.
- **Segunda persona**: habla de *tu equipo*, *tu negocio*, *tus procesos* — no de
  "las empresas" en abstracto.

## Qué vender

Vende **el resultado**, no la tecnología. El cliente no compra agentes de IA: compra
tiempo recuperado, costes que bajan y poder crecer sin contratar.

- ✅ "Recupera cientos de horas al mes"
- ❌ "Implementamos arquitecturas multiagente con LLMs de última generación"

Sé concreto con el beneficio y con el mecanismo:

- ✅ "Prospectan, cualifican y contactan clientes por ti, 24/7."
- ❌ "Optimizamos tu proceso comercial de forma integral."

## Prohibido

- Palabras de relleno corporativo: *sinergia*, *holístico*, *solución integral*,
  *disruptivo*, *revolucionario*, *innovador*, *de última generación*.
- Promesas sin número ni mecanismo ("multiplicamos tus ventas").
- Nombres de tecnologías o proveedores en el copy público (GPT, n8n, Django…): al
  cliente le da igual con qué está hecho.
- Signos de exclamación múltiples y mayúsculas para enfatizar.
- Emojis en el cuerpo del texto. Solo se usan como icono de servicio, en el campo `icon`.

## Formato por tipo de texto

| Elemento | Extensión objetivo |
|---|---|
| Titular de hero | 8–14 palabras, una sola idea |
| Subtítulo de hero | 1–2 frases, máximo 30 palabras |
| Título de sección | 3–7 palabras |
| Título de servicio | 4–8 palabras |
| Descripción de servicio | 2 frases, 20–35 palabras |
| Propuesta de valor | Título de 2–3 palabras + 1–2 frases |
| Llamada a la acción | Verbo en primera persona ("Quiero mi diagnóstico gratuito") |

Las llamadas a la acción se escriben desde la voz del visitante, no de la empresa:
"Quiero mi diagnóstico gratuito" funciona mejor que "Solicita información".

## Antes de dar por bueno un texto

1. ¿Se entiende sin saber nada de IA?
2. ¿Dice qué gana el cliente, no qué hacemos nosotros?
3. ¿Sobra alguna palabra? Quítala y relee.
4. ¿Encaja en la extensión de la tabla?
5. ¿Hay algún test que compare contra ese texto? No pasa nada: los tests leen de
   `content.*`, así que se actualizan solos. Ejecuta
   `.venv/Scripts/python.exe manage.py test apps` para confirmarlo.
