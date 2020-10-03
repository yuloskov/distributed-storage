from django.conf import settings
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError
from main.models import (
    Storage,
    File,
)
import os
import time
import requests

LOGS_PATH = 'LOGS.txt'
STORAGE_SERVER_PORT = os.environ['STORAGE_SERVER_PORT']


class Command(BaseCommand):
    help = 'Start server monitoring'

    def add_arguments(self, parser):
        parser.add_argument('--repeat', type=int, default=10)

    def health_check(self):
        logs = open(LOGS_PATH, 'a+')
        for s in Storage.objects.all():
            try:
                status = requests.get(
                    f'http://{s.ip}:{STORAGE_SERVER_PORT}/status',
                    timeout=3
                ).text

                logs.write(f'{s.ip} : {status}\n')
            except requests.exceptions.Timeout:
                # Remove the server
                s.delete()
                # Replicate files with < required num of copies
                need_to_replicate = File.objects.annotate(
                    num_replicas=Count('storage')
                ).filter(num_replicas__lt=settings.NUM_OF_REPLICAS)

                for f in need_to_replicate:
                    file_servers = f.storage.all()
                    if len(file_servers) == 0:
                        logs.write(f'File {f.file_path} lost forever')
                    init_server = file_servers[0]
                    logs.write(
                        f'Replicatting {f.file_path}. Starting from {init_server.ip}\n')
                    response = requests.post(
                        f'http://{init_server.ip}:{STORAGE_SERVER_PORT}/replicate',
                        data={'file_path': f.file_path}
                    )

                logs.write(f'{s.ip} : FAIL\n')

        logs.write('\n')
        logs.close()

    def handle(self, *args, **options):
        if os.path.exists(LOGS_PATH):
            os.remove(LOGS_PATH)

        print('Start monitoring')
        repeat = options['repeat']
        while True:
            self.health_check()
            time.sleep(repeat)
