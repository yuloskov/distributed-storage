import os
import errno
import requests
import subprocess
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
storage_server_port = os.environ['STORAGE_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}/'
file_url = f'{name_server_url}api/file/'

save_folder = '/save_folder/'


@app.route('/status')
def status():
    return 'OK'


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 400

        file = request.files['file']
        if not file:
            return 400

        if 'file_path' not in request.form:
            return 400

        file_path = request.form['file_path']
        print(file_path)
        save_path = os.path.join(save_folder, file_path)
        print(save_path)

        if not os.path.exists(os.path.dirname(save_path)):
            try:
                os.makedirs(os.path.dirname(save_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        file.save(save_path)
        print('File saved locally')

        print('Writing file to db')
        save_file_to_db(file_path)
        print('Saved file to db')

        replicate_file(file_path)
        return 'File received'


@app.route('/delete', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        if 'file_path' not in request.form:
            return 404

        file_path = request.form['file_path']
        file_path = os.path.join(save_folder, file_path)
        os.remove(file_path)
        return 200


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
    storage_id = get_storage_id(container_ip)

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

    response = requests.get(f'{file_url}{file_id}/replicate_ip/')
    return response.json()[0]['ip']


def replicate_file(file_path):
    ip = get_replicate_ip(file_path)
    print('replicate ', ip)
    print(file_path)
    save_path = os.path.join(save_folder, file_path)
    send_data_to_server(save_path, ip)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
