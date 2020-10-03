import os
import requests
import subprocess


def register():
    # TODO change for machine ip
    # Get container ip
    result = subprocess.run(
        ['awk', 'END{print $1}', '/etc/hosts'],
        stdout=subprocess.PIPE,
    )
    container_ip = result.stdout.decode('utf-8').strip()
    print(container_ip)
    print(ip)
    print(port)

    response = requests.post(
        f'http://{ip}:{port}/api/storage/',
        data={'ip': container_ip},
    )
    print(response.status_code)


if __name__ == '__main__':
    print(os.environ)
    ip = os.environ['NAME_SERVER_IP']
    port = os.environ['NAME_SERVER_PORT']
    register()
