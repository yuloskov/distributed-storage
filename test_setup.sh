cd ./storage_server
docker kill storage1
docker rm storage1
docker build -t storage1 .
docker run -d --name=storage1 --env-file=.env storage1
docker network connect name_server_default storage1

docker kill storage2
docker rm storage2
docker build -t storage2 .
docker run -d --name=storage2 --env-file=.env storage2
docker network connect name_server_default storage2

cd ../client
docker kill client1
docker rm client1
docker build -t client1 .
docker run -d --name=client1 --env-file=.env -v $(pwd)/upload_folder:/upload_folder client1
docker network connect name_server_default client1