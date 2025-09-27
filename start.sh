#!/bin/bash

# Set Django settings module
export DJANGO_SETTINGS_MODULE=config.settings_production

# Wait for database to be ready
echo "Waiting for database..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting EspritVerse..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers=${WEB_CONCURRENCY:-2} --timeout ${GUNICORN_TIMEOUT:-120}