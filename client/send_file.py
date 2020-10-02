import os
import sys
import requests

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}/'

storage_server_port = os.environ['STORAGE_SERVER_PORT']


def send_data_to_server(filepath, ip):
    filename = os.path.basename(filepath)
    multipart_form_data = {
        'file': (filename, open(filepath, 'rb')),
    }
    response = requests.post(
        f'http://{ip}:{storage_server_port}/',
        files=multipart_form_data,
    )
    print(response.status_code)


def get_server_ip():
    response = requests.get(f'{name_server_url}api/storage/available')
    print(response.status_code)
    print(response.json())
    print(response.json())
    return response.json()[0]['ip']


def main(argv):
    if len(sys.argv) != 2:
        print(f'Usage: {argv[0]} filename')
        exit(1)

    filename = argv[1]
    ip = get_server_ip()
    print(f'[+] Connecting to {ip}')
    send_data_to_server(filename, ip)
    print('[+] Connected.')


if __name__ == '__main__':
    main(sys.argv)
