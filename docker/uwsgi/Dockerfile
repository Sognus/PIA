FROM alpine:3.7

ADD ./application /app
ADD ./docker /app/docker

WORKDIR /app

RUN \
    apk add --update python3 uwsgi uwsgi-python3 && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/docker/uwsgi/requirements.txt

EXPOSE 3031

CMD ["uwsgi", "--ini", "/app/application.ini", "--plugin", "python3"]
