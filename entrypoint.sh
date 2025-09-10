#!/usr/bin/env bash
set -e

# Optional: run Django checks
python manage.py check --deploy

# Migrate & collect static
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn on Fly's expected port 8080 (using your project module)
exec gunicorn testaurant_app_crud.wsgi:application \
  --bind 0.0.0.0:8080 \
  --workers 3 \
  --timeout 60