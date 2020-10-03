import os
import sys
import requests

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}/'

storage_server_port = os.environ['STORAGE_SERVER_PORT']


def send_data_to_server(file_path, ip):
    filename = os.path.basename(file_path)
    multipart_form_data = {
        'file': (filename, open(file_path, 'rb')),
    }
    file_path_send = os.path.join(*(file_path.split(os.path.sep)[2:]))
    response = requests.post(
        f'http://{ip}:{storage_server_port}/upload',
        files=multipart_form_data,
        data={'file_path': file_path_send},
    )
    print(response.status_code)


def get_server_ip():
    response = requests.get(f'{name_server_url}api/storage/available/')
    return response.json()[0]['ip']


def main(argv):
    if len(sys.argv) != 2:
        print(f'Usage: {argv[0]} filename')
        exit(1)

    file_path = argv[1]
    ip = get_server_ip()
    print(f'[+] Sending to {ip}')
    send_data_to_server(file_path, ip)
    print('[+] File has been sent.')


if __name__ == '__main__':
    main(sys.argv)
