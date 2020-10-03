from django.core.management.base import BaseCommand, CommandError
import time

class HealthCheck(BaseCommand):
    help = 'Start server monitoring'

    def handle(self, *args, **options):
        print('Start monitoring')
        while True:
            time.sleep(3)
            with open('/LOGS.txt', 'a+') as f:
                f.write('DATA\n')
