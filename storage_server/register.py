import os
import requests


def register():
    response = requests.post(f'http://{ip}:{port}/api/storage/')
    print(response.status_code)


if __name__ == '__main__':
    print(os.environ)
    ip = os.environ['NAME_SERVER_IP']
    port = os.environ['NAME_SERVER_PORT']
    register()
