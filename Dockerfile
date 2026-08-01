FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

EXPOSE 8000

CMD python manage.py migrate --run-syncdb && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000
