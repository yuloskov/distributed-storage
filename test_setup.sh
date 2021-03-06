#!/bin/bash

NAME_SEVER_NETWORK=name_server_default


cd ./storage_server
docker kill storage1
docker rm storage1
docker build -t storage1 .
docker run -d --name=storage1 --env-file=.env storage1
docker network connect ${NAME_SEVER_NETWORK} storage1

docker kill storage2
docker rm storage2
docker build -t storage2 .
docker run -d --name=storage2 --env-file=.env storage2
docker network connect ${NAME_SEVER_NETWORK} storage2

docker kill storage3
docker rm storage3
docker build -t storage3 .
docker run -d --name=storage3 --env-file=.env storage3
docker network connect ${NAME_SEVER_NETWORK} storage3

cd ../client
docker kill client1
docker rm client1
docker build -t client1 .
docker create -it --name=client1 --env-file=.env -v $(pwd)/upload_folder:/upload_folder client1
docker network connect ${NAME_SEVER_NETWORK} client1
docker start -ia client1
