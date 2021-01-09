FROM alpine:3.7

# Create directory /app
RUN mkdir /app

# COPY files for build
COPY ./application/requirements.txt /app/requirements.txt
COPY ./application/gunicorn.conf.py /app/gunicorn.conf.py 

# COPY container entry point to container
COPY ./docker/asgi/entrypoint.sh /entrypoint.sh

# SET entry point script as runnable
RUN chmod +x /entrypoint.sh

# Work in /app folder
WORKDIR /app

# Prepare envinroment
RUN \
    apk add --update postgresql-dev gcc python3-dev musl-dev make libffi-dev && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/requirements.txt

# ADD APP to container
VOLUME /app

# Make port 8000 public
EXPOSE 8000

# Set container entry point
ENTRYPOINT ["/entrypoint.sh"]
