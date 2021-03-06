import hashlib
import os
import errno
import requests
from flask import Flask, request, send_file


app = Flask(__name__)

name_server_ip = os.environ['NAME_SERVER_IP']
name_server_port = os.environ['NAME_SERVER_PORT']
storage_server_port = os.environ['STORAGE_SERVER_PORT']
private_ip = os.environ['PRIVATE_IP']
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


@app.route('/replicate', methods=['POST'])
def replicate():
    dest_ip = request.form.get('dest_ip')
    file_path = request.form.get('file_path')
    print(file_path)
    save_path = os.path.join(save_folder, file_path)
    send_data_to_server(save_path, file_path, dest_ip)
    return 'OK'


@app.route('/file', methods=['DELETE', 'GET', 'POST'])
def file():
    if request.method == 'GET':
        file_path = request.args.get('file_path')
        save_path = os.path.join(save_folder, file_path)
        return send_file(save_path)
    elif request.method == 'POST':
        if 'file' not in request.files:
            return 'No file sent', 400

        file = request.files['file']
        if not file:
            return 'Bad file', 400

        if 'file_path' not in request.form:
            return 'No file path', 400

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
        file_size = round(os.path.getsize(save_path)/(1024*1024), 2)
        save_file_to_db(file_path, file_hash, file_size)
        print('Saved file to db')

        return ''
    elif request.method == 'DELETE':
        file_path = request.args.get('file_path')
        file_path = os.path.join(save_folder, file_path)
        os.remove(file_path)
        return ''
    return 'Invalid method', 400


@app.route('/dump_tree', methods=['GET'])
def list_files():
    res = {}
    for dir_path, dir_names, file_names in os.walk(save_folder):
        for file_name in file_names:
            path = os.path.join(dir_path, file_name)
            sub_path = path[len(save_folder):]
            res[sub_path] = {
                "hash": md5(path),
                "size": round(os.path.getsize(path)/(1024*1024), 2)
            }
    return res


def send_data_to_server(save_path, file_path, ip):
    filename = os.path.basename(file_path)
    multipart_form_data = {
        'file': (filename, open(save_path, 'rb')),
    }
    response = requests.post(
        f'http://{ip}:{storage_server_port}/file',
        files=multipart_form_data,
        data={'file_path': file_path},
    )
    print(response.status_code)


def save_file_to_db(file_path, file_hash, file_size):
    response = requests.post(
        file_url,
        data={'file_path': file_path, 'file_hash': file_hash, 'file_size': file_size, 'private_ip': private_ip},
    )
    print(response.status_code)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
