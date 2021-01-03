#!/bin/ash

# Wait for database start
while ! nc -z database 5432; do sleep 1; done;

# Setup Django   
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate

# Run ASGI - gunicorn server
#gunicorn application.asgi:application --reload --bind 0.0.0.0 -k uvicorn.workers.UvicornWorker
gunicorn application.asgi:application --config gunicorn.conf.py