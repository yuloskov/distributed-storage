import os
import requests

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}'

storage_server_port = os.environ['STORAGE_SERVER_PORT']


def upload_file(rel_path, abs_path):
    print('[+] Choosing random initial storage')
    ip = get_server_ip()
    print(f'[+] Sending to {ip}')
    filename = os.path.basename(rel_path)
    multipart_form_data = {
        'file': (filename, open(abs_path, 'rb')),
    }
    requests.post(
        f'http://{ip}:{storage_server_port}/upload',
        files=multipart_form_data,
        data={'file_path': rel_path},
    )
    print('[+] File has been sent.')


def get_server_ip():
    response = requests.get(f'{name_server_url}/api/v1/storage/available/')
    return response.json()['ip']


def delete_file(rel_path):
    print(f'[+] Deleting {rel_path}')
    requests.delete(
        f'{name_server_url}/api/v1/file/',
        data={"file_path": rel_path}
    )
    print('[+] File has been deleted.')
