# distributed-storage
awk 'END{print $1}' /etc/hosts

docker build -t storage1 .
docker run -d --name=storage1 --env-file=.env storage1
docker network connect name_server_default storage1

docker build -t client1 .
docker run -d --name=client1 --env-file=.env -v /home/yuloskov/PycharmProjects/DSS/storage/client/upload_folder:/upload_folder client1
docker network connect name_server_default client1


