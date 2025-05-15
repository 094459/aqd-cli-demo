#!/bin/bash
set -e

# Wait for potential database to be ready (if using external database)
# Uncomment if needed
# until nc -z -v -w30 $DATABASE_HOST $DATABASE_PORT; do
#   echo "Waiting for database connection..."
#   sleep 2
# done

# Apply database migrations if needed
# Uncomment if using Flask-Migrate
# flask db upgrade

# Initialize the database
python -c "from src.app import create_app; app = create_app(); app.app_context().push(); from src.extensions import db; db.create_all()"

# Check if we're in development mode
if [ "${FLASK_ENV}" = "development" ]; then
  echo "Starting Flask development server..."
  python run.py
else
  echo "Starting Gunicorn server..."
  # Use the gunicorn config if it exists, otherwise use reasonable defaults
  if [ -f "gunicorn_config.py" ]; then
    exec gunicorn -c gunicorn_config.py wsgi:app
  else
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
      --workers ${GUNICORN_WORKERS:-3} \
      --access-logfile - \
      --error-logfile - \
      wsgi:app
  fi
fi
