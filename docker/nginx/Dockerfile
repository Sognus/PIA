FROM alpine:3.7

# Add files to container
VOLUME /app

# Work in /app folder
WORKDIR /app

# Install and update NGINX
RUN \
    apk add --update nginx

# Clear default configurations
RUN \
    rm /etc/nginx/conf.d/default.conf && \
    mkdir -p /run/nginx && \
    ln -s /dev/stderr /var/log/nginx/error.log && \
    ln -s /dev/stdout /var/log/nginx/access.log

# ADD nginx configuration to container
COPY docker/nginx/application.conf /etc/nginx/conf.d/application.conf

# ADD container entry point to container
COPY docker/nginx/entrypoint.sh /entrypoint.sh

# SET entry point script as runnable
RUN chmod +x /entrypoint.sh

# Make port 80 public
EXPOSE 80

# Set container entry point
ENTRYPOINT ["/entrypoint.sh"]
