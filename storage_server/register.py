import os
import requests
import subprocess

ip = os.environ['NAME_SERVER_IP']
port = os.environ['NAME_SERVER_PORT']


def register():
    # TODO change for machine ip
    # Get container ip
    result = subprocess.run(
        ['awk', 'END{print $1}', '/etc/hosts'],
        stdout=subprocess.PIPE,
    )
    container_ip = result.stdout.decode('utf-8').strip()

    response = requests.post(
        f'http://{ip}:{port}/api/storage/',
        data={'ip': container_ip},
    )
    print(response.status_code)


if __name__ == '__main__':
    register()
