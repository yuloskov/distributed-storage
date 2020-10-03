NAME_SEVER_NETWORK=name_server_default

cd ./storage_server
docker kill storage1
docker rm storage1

docker kill storage2
docker rm storage2

docker kill storage3
docker rm storage3

cd ../client
docker kill client1
docker rm client1
