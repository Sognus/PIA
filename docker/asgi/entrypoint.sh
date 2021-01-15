#!/bin/ash

# Wait for database start
while ! nc -z database 5432; do sleep 1; done;

# Setup Django   
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser \
	--username "admin@admin.cz" \
	--email "admin@admin.cz"  \
	--noinput

# Run ASGI server
#gunicorn pia.asgi:application --reload --bind 0.0.0.0 -k uvicorn.workers.UvicornWorker
#gunicorn pia.asgi:application --config gunicorn.conf.py
#uvicorn --host 0.0.0.0 --port 8000 --reload --ws websockets --reload-dir /app  pia.asgi:application
daphne -b 0.0.0.0 -p 8000 pia.asgi:application
