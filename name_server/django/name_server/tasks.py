from django.dispatch import receiver

from .models import (
    File,
    Storage,
)
from .signals import (
    file_saved,
    storage_up,
    storage_down,
)
from .utils import (
    replicate_all,
    replicate_file,
)

import os
import requests

import logging

logger = logging.getLogger(__name__)

# ----------- SIGNAL HANDLERS -----------
STORAGE_SERVER_PORT = os.environ['STORAGE_SERVER_PORT']


@receiver(file_saved)
def replicate_on_file_save(sender, **kwargs):
    file = kwargs['file']
    replicate_file(file)


@receiver(storage_down)
def replicate_on_storage_down(sender, **kwargs):
    storage = kwargs['storage']
    # Replicate files that were on the failed storage
    for f in storage.files.all():
        logger.info(f'STARTING REPLICATION OF FILE {f.file_path}')
        replicate_file(f)


@receiver(storage_up)
def sync_on_storage_up(sender, **kwargs):
    storage = kwargs['storage']

    if File.objects.count() == 0:
        return

    s_ip = storage.private_ip

    storage_files = requests.get(f'http://{s_ip}:{STORAGE_SERVER_PORT}/dump_tree').json()
    logger.info(storage_files)
    for p in storage_files:
        file = File.objects.filter(file_path=p).first()
        if file is None or file.hash != storage_files[p]['hash']:
            requests.delete(f'http://{s_ip}:{STORAGE_SERVER_PORT}/file', params={"file_path": p})
    replicate_all()


# ----------- DJANGO Q HANDLERS -----------
def file_replication_check(file_pk, storage_pk):
    file = File.objects.get(pk=int(file_pk))
    storage = Storage.objects.get(pk=int(storage_pk))

    # Successful replication
    if file.storage.filter(pk=storage.pk).exists():
        logger.info(f'Succ repl check {file.file_path} {storage.private_ip}')
    # Something went wrong
    # Try to replicate again
    else:
        replicate_file(file)
