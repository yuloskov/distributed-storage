#!/bin/bash

# docker-machine create master
# docker-machine create storage1
# docker-machine create storage2
# docker-machine create storage3

# docker-machine create --driver amazonec2 --amazonec2-open-port 5000 --amazonec2-open-port 8000 aws-master
# docker-machine create --driver amazonec2 --amazonec2-open-port 5000 --amazonec2-open-port 8000 aws-storage1
# docker-machine create --driver amazonec2 --amazonec2-open-port 5000 --amazonec2-open-port 8000 aws-storage2
# docker-machine create --driver amazonec2 --amazonec2-open-port 5000 --amazonec2-open-port 8000 aws-storage3

# MASTER_IP=$(docker-machine ip aws-master)
# docker-machine ssh aws-master sudo docker swarm init --advertise-addr "$MASTER_IP"
# TOKEN=$(docker-machine ssh aws-master sudo docker swarm join-token -q worker)
# docker-machine ssh aws-storage1 sudo docker swarm join --token "$TOKEN" "$MASTER_IP:2377"
# docker-machine ssh aws-storage2 sudo docker swarm join --token "$TOKEN" "$MASTER_IP:2377"
# docker-machine ssh aws-storage3 sudo docker swarm join --token "$TOKEN" "$MASTER_IP:2377"

# docker-machine ssh aws-master sudo docker node update --label-add primary=true aws-master

# docker-machine ssh aws-storage1 sudo mkdir -p /save_folder
# docker-machine ssh aws-storage2 sudo mkdir -p /save_folder
# docker-machine ssh aws-storage3 sudo mkdir -p /save_folder

# docker-machine ssh aws-storage1 curl http://169.254.169.254/latest/meta-data/public-ipv4 > /home/ubuntu/ip
# docker-machine ssh aws-storage2 curl http://169.254.169.254/latest/meta-data/public-ipv4 > /home/ubuntu/ip
# docker-machine ssh aws-storage3 curl http://169.254.169.254/latest/meta-data/public-ipv4 > /home/ubuntu/ip

# cat docker-compose.deploy.yaml | docker-machine ssh aws-master sudo docker stack deploy -c - app

# docker-machine ssh aws-master sudo docker exec -e DJANGO_SUPERUSER_PASSWORD=12345678 app_django.1.$(docker-machine ssh aws-master sudo docker service ps -f 'name=app_django.1' app_django -q --no-trunc | head -n1) python3 manage.py createsuperuser --noinput --username root --email root@example.com
