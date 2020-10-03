import os
import sys
import requests

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}/'
file_url = f'{name_server_url}api/file/'


def delete_file(file_path):
    file_path_send = os.path.join(*(file_path.split(os.path.sep)[2:]))
    response = requests.get(
        f'{file_url}id/',
        params={'file_path': file_path_send},
    )
    file_id = response.json()['id']
    print(file_id)

    response = requests.delete(f'{file_url}{file_id}/')
    print(response.status_code)


def main(argv):
    if len(sys.argv) != 2:
        print(f'Usage: {argv[0]} save_path')
        exit(1)

    file_path = argv[1]
    print(f'[+] Deleting {file_path}')
    delete_file(file_path)
    print('[+] File has been deleted.')


if __name__ == '__main__':
    main(sys.argv)
