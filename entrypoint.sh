#!/bin/sh
set -e

until python manage.py migrate --noinput
do
    echo "Waiting for postgres..."
    sleep 2
done

python manage.py load_tags
python manage.py load_ingredients

python manage.py collectstatic --noinput

cp -r /app/collected_static/. /django_static/static/

gunicorn --bind 0.0.0.0:8000 cookbook.wsgi:application