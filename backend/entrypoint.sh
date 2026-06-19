#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin user..."
python scripts/create_admin.py

# 可选：初始化演示数据（设置 SEED_DEMO=true 时执行，幂等）
if [ "${SEED_DEMO}" = "true" ]; then
    echo "Seeding demo data..."
    python manage.py seed_demo || echo "seed_demo failed (non-fatal)"
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
