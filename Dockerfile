FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

# Usuario sin privilegios: si alguien explota la app, no es root en el contenedor.
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# check --deploy aborta el arranque si falta configuración crítica de producción.
# --threads: cada mensaje del chat espera varios segundos la respuesta de n8n;
# con hilos, esa espera no deja al resto de visitantes sin worker libre.
CMD ["sh", "-c", "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py check --deploy --fail-level ERROR && \
    gunicorn config.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      --threads 4 \
      --timeout 60 \
      --access-logfile - \
      --error-logfile - \
      --forwarded-allow-ips '*'"]
