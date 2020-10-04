from django.core.management.base import BaseCommand

from name_server.models import (
    Storage,
)
from name_server.signals import storage_up, storage_down

import os
import time
import requests

STORAGE_SERVER_PORT = os.environ['STORAGE_SERVER_PORT']


class Command(BaseCommand):
    help = 'Start server monitoring'

    def add_arguments(self, parser):
        parser.add_argument('--repeat', type=int, default=10)

    def health_check(self):
        # logs = open(settings.LOGS_PATH, 'a+')
        for s in Storage.objects.all():
            try:
                status = requests.get(
                    f'http://{s.ip}:{STORAGE_SERVER_PORT}/status',
                    timeout=3
                ).text
                if s.status != 'UP':
                    s.status = 'UP'
                    s.save()
                    storage_up.send(sender=None)

                # logs.write(f'{s.ip} : {status}\n')
            except requests.exceptions.Timeout:
                # Remove the server
                if s.status != 'DN':
                    s.status = 'DN'
                    s.save()
                    storage_down.send(sender=None)
                # logs.write(f'{s.ip} : FAIL\n')

                # Send replication signal


        # logs.write('\n')
        # logs.close()

    def handle(self, *args, **options):
        # if os.path.exists(LOGS_PATH):
        #     os.remove(LOGS_PATH)

        print('Start monitoring')
        repeat = options['repeat']
        while True:
            self.health_check()
            time.sleep(repeat)