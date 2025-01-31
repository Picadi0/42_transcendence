FROM nginx:1.27.3-alpine-slim

RUN apk add --no-cache openssl bash

# SSL Sertifikası oluşturma (Mevcutsa yeniden oluşturulmaz)
RUN mkdir -p /etc/nginx/ssl && \
    if [ ! -f /etc/nginx/ssl/myself-sign.key ]; then \
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/myself-sign.key \
        -out /etc/nginx/ssl/myself-sign.crt \
        -subj "/C=TR/ST=Istanbul/L=Istanbul/O=bro/OU=Development/CN=localhost"; \
    fi

COPY ./nginx.conf.template /etc/nginx/nginx.conf.template

# nginx.conf dosyasında envsubst kullanılmadan nginx başlat
CMD cp /etc/nginx/nginx.conf.template /etc/nginx/nginx.conf && nginx -g 'daemon off;'

EXPOSE 80 443
