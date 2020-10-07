import os
import requests


def register(ns_ip, port, public_ip):
    response = requests.post(
        f'http://{ns_ip}:{port}/api/v1/storage/',
        data={'public_ip': public_ip}
    )
    print(response.status_code)


if __name__ == '__main__':
    ns_ip = os.environ['NAME_SERVER_IP']
    port = os.environ['NAME_SERVER_PORT']
    public_ip = os.environ['PUBLIC_IP']
    register(ns_ip, port, public_ip)
