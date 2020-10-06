#!/bin/bash

# docker-machine create master
# docker-machine create storage1
# docker-machine create storage2
# docker-machine create storage3

# MASTER_IP=$(docker-machine ip master)
# docker-machine ssh master docker swarm init --advertise-addr "$MASTER_IP"
# TOKEN=$(docker-machine ssh master docker swarm join-token -q worker)
# docker-machine ssh storage1 docker swarm join --token "$TOKEN" "$MASTER_IP:2377"
# docker-machine ssh storage2 docker swarm join --token "$TOKEN" "$MASTER_IP:2377"
# docker-machine ssh storage3 docker swarm join --token "$TOKEN" "$MASTER_IP:2377"

# docker-machine ssh master docker node update --label-add primary=true master

# docker-machine ssh storage1 sudo mkdir -p /save_folder
# docker-machine ssh storage2 sudo mkdir -p /save_folder
# docker-machine ssh storage3 sudo mkdir -p /save_folder

# cat docker-compose.deploy.yaml | docker-machine ssh master docker stack deploy -c - app

# docker-machine ssh master docker exec -e DJANGO_SUPERUSER_PASSWORD=12345678 app_django.1.$(docker-machine ssh master docker service ps -f 'name=app_django.1' app_django -q --no-trunc | head -n1) python3 manage.py createsuperuser --noinput --username root --email root@example.com
