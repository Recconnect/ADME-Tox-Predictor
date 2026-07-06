FROM nginx:1.27-alpine

RUN apk add --no-cache certbot certbot-nginx

COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY landing/ /var/www/admetox/landing/

EXPOSE 80 443
