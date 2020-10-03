import os
import requests
import subprocess
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
storage_server_port = os.environ['STORAGE_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}/'
file_url = f'{name_server_url}api/file/'


@app.route('/status')
def status():
    return 'OK'


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join('/save_folder', filename)
            file.save(save_path)
            print('File saved locally')

            print('Writing file to db')
            save_file_to_db(save_path)
            print('Saved file to db')

            replicate_file(save_path)
            return 'File received'


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


def get_storage_id(ip):
    response = requests.get(
        f'{name_server_url}api/storage/id/',
        params={'ip': ip},
    )
    return response.json()['id']


def save_file_to_db(save_path):
    # TODO change for server ip in future
    # Get container ip
    result = subprocess.run(
        ['awk', 'END{print $1}', '/etc/hosts'],
        stdout=subprocess.PIPE,
    )
    container_ip = result.stdout.decode('utf-8').strip()

    print(container_ip)
    storage_id = get_storage_id(container_ip)
    print(storage_id)

    response = requests.post(
        file_url,
        data={'file_path': save_path, 'storage': storage_id},
    )
    print(response.status_code)


def get_replicate_ip(save_path):
    response = requests.get(
        f'{file_url}id/',
        params={'file_path': save_path},
    )
    file_id = response.json()['id']
    print(file_id)

    response = requests.get(f'{file_url}{file_id}/replicate_ip/')
    print(response.json())
    return response.json()[0]['ip']


def replicate_file(save_path):
    ip = get_replicate_ip(save_path)
    print('replicate ', ip)
    print(save_path)
    send_data_to_server(save_path, ip)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
