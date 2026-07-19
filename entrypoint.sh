#!/bin/sh
set -e

echo "Waiting for database..."
python <<'PY'
import os
import time
import psycopg

url = os.environ.get("DATABASE_URL", "")
# DATABASE_URL uses postgres:// which psycopg accepts as postgresql://
dsn = url.replace("postgres://", "postgresql://", 1)
for attempt in range(30):
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
        break
    except Exception as exc:
        print(f"DB not ready ({attempt + 1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${RUN_SEED:-false}" = "true" ]; then
  python manage.py seed_demo
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
