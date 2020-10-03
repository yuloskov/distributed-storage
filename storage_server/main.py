import hashlib
import os
import errno
import requests
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
storage_server_port = os.environ['STORAGE_SERVER_PORT']
name_server_url = f'http://{name_server_ip}:{name_server_port}'
file_url = f'{name_server_url}/api/v1/file/'

save_folder = '/save_folder/'


def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route('/status')
def status():
    return 'OK'


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method != 'POST':
        return

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
    file_hash = md5(save_path)
    save_file_to_db(file_path, file_hash)
    print('Saved file to db')

    return 'File received'


@app.route('/replicate', methods=['POST'])
def replicate():
    if request.method != 'POST':
        return
    dest_ip = request.form.get('dest_ip')
    file_path = request.form.get('file_path')
    print(file_path)
    save_path = os.path.join(save_folder, file_path)
    send_data_to_server(save_path, file_path, dest_ip)
    return 'OK'


@app.route('/delete', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        if 'file_path' not in request.form:
            return 404

        file_path = request.form['file_path']
        file_path = os.path.join(save_folder, file_path)
        os.remove(file_path)
        return 200


def send_data_to_server(save_path, file_path, ip):
    filename = os.path.basename(file_path)
    multipart_form_data = {
        'file': (filename, open(save_path, 'rb')),
    }
    response = requests.post(
        f'http://{ip}:{storage_server_port}/upload',
        files=multipart_form_data,
        data={'file_path': file_path},
    )
    print(response.status_code)


def save_file_to_db(file_path, file_hash):
    response = requests.post(
        file_url,
        data={'file_path': file_path, 'file_hash': file_hash},
    )
    print(response.status_code)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
