import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/status')
def status():
    return 'OK'


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('/save_folder', filename))
            return 'File received'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
