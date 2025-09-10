#!/usr/bin/env bash
set -Eeuo pipefail

echo "[entrypoint] Starting container"
echo "[entrypoint] Working dir: $(pwd)"
echo "[entrypoint] Python: $(python -V)"
echo "[entrypoint] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<unset>}"
echo "[entrypoint] PORT env=${PORT:-<unset>} (Fly will provide this; defaulting to 8080)"

# Default PORT if not set
PORT="${PORT:-8080}"

echo "[entrypoint] Running Django system checks"
python manage.py check --deploy || true

echo "[entrypoint] Applying migrations"
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files"
python manage.py collectstatic --noinput

echo "[entrypoint] Launching Gunicorn on 0.0.0.0:${PORT}"
exec gunicorn testaurant_app_crud.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers 3 \
  --timeout 60