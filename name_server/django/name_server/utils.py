from django.conf import settings
from django.db.models import Count, Q

from .models import (
    File,
    Storage,
)

import os
import requests
from datetime import datetime, timedelta

from django_q.tasks import schedule

import logging

logger = logging.getLogger(__name__)


STORAGE_SERVER_PORT = os.environ['STORAGE_SERVER_PORT']


def replicate_file(f):
    file_servers = f.storage.filter(status='UP')

    # TODO what if the file has enough replicas?
    init_server = file_servers.first()
    copy_to = Storage.objects.filter(status='UP').difference(file_servers).first()

    if init_server is None or copy_to is None:
        return

    try:
        requests.post(
            f'http://{init_server.ip}:{STORAGE_SERVER_PORT}/replicate',
            data={
                'file_path': f.file_path,
                'dest_ip': copy_to.ip
            }
        )
    except:
        pass

    # Schedule replication check
    next_run = datetime.now() + timedelta(seconds=10)
    schedule(
        'name_server.tasks.file_replication_check',
        f.pk, copy_to.pk,
        next_run=next_run,
        repeats=1,
    )


def replicate_all():
    need_to_replicate = File.objects.annotate(
        num_replicas=Count('storage', filter=Q(storage__status='UP'))
    ).filter(num_replicas__lt=settings.NUM_OF_REPLICAS)

    for f in need_to_replicate:
        replicate_file(f)


