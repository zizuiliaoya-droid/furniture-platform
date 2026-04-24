#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin user..."
python scripts/create_admin.py

echo "Starting Gunicorn..."
exec gunicorn config.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
