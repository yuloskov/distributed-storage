FROM nginx:1.17

VOLUME ["/tmp/sockets", "/var/www/static", "/var/www/media"]

COPY config /etc/nginx

CMD ["nginx", "-g", "daemon off;"]

EXPOSE "8000"