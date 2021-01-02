FROM alpine:3.7

# Create directory /app
RUN mkdir /app

# ADD web application files to container
ADD ./application /app
VOLUME /app

# ADD other files to container
ADD docker/uwsgi/requirements.txt /app


# Work in /app folder
WORKDIR /app

# Prepare envinroment
RUN \
    apk add --update postgresql-dev gcc python3-dev musl-dev && \
    apk add --update python3 uwsgi uwsgi-python3 && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/requirements.txt

# ADD container entry point to container
COPY docker/uwsgi/entrypoint.sh /entrypoint.sh

# SET entry point script as runnable
RUN chmod +x /entrypoint.sh

# Make port 3301 public
EXPOSE 3031

# Set container entry point
ENTRYPOINT ["/entrypoint.sh"]
