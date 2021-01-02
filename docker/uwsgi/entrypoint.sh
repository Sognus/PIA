#!/bin/ash
# Wait for database start
while ! nc -z database 5432; do sleep 1; done;

# Setup Django   
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate

# Run UWSGI
uwsgi --ini /app/application.ini --plugin python3