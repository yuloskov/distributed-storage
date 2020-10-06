import hashlib
import os
import requests

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}'

storage_server_port = os.environ['STORAGE_SERVER_PORT']


def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(rel_path, abs_path):
    print('[+] Choosing random initial storage')
    ip = get_server_ip()
    print(f'[+] Sending to {ip}')
    filename = os.path.basename(rel_path)
    multipart_form_data = {
        'file': (filename, open(abs_path, 'rb')),
    }
    requests.post(
        f'http://{ip}:{storage_server_port}/file',
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
        params={"file_path": rel_path}
    )
    print('[+] File has been deleted.')


def list_files(dir_path):
    response = requests.get(
        f'{name_server_url}/api/v1/ls/',
        params={"dir_path": dir_path}
    )
    return response.json()


def download_file(rel_path, abs_path):
    print(f'[+] Choosing storage which has the {rel_path} file')
    response = requests.get(f'{name_server_url}/api/v1/file/', params={"file_path": rel_path})
    ip = response.json()['ip']
    print(f'[+] Downloaing from {ip}')
    response = requests.get(f'http://{ip}:{storage_server_port}/file', params={"file_path": rel_path})
    if response.status_code != 200:
        print(f'Failed to download file, HTTP code {response.status_code}')
        return
    open(abs_path, 'wb').write(response.content)
    print('[+] File has been saved.')
