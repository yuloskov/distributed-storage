import os
import sys
import requests

ip = os.environ['NAME_SERVER_IP']
port = os.environ['NAME_SERVER_PORT']


def register(container_ip):
    response = requests.post(f'http://{ip}:{port}/api/storage/',
                             data={'ip': container_ip})
    print(response.status_code)


def main(argv):
    if len(sys.argv) != 2:
        print(f'Usage: {argv[0]} container_ip')
        exit(1)

    container_ip = argv[1]
    print(f'[+] Connecting to {ip}')
    register(container_ip)
    print('[+] Connected.')


if __name__ == '__main__':
    main(sys.argv)