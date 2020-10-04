from django.conf import settings

from logging import log
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

import logging

logger = logging.getLogger(__name__)

# ----------- SIGNAL HANDLERS -----------
@receiver(file_saved)
def replicate_on_file_save(sender, **kwargs):
    file = kwargs['file']
    storage = kwargs['storage']

    if file.storage.count() < settings.NUM_OF_REPLICAS:
        logger.info(f'REPLICATING {file.file_path}')
        replicate_file(file)
    else:
        logger.info(f'ENOUGH COPIES {file.file_path}')


@receiver(storage_down)
def replicate_on_storage_down(sender, **kwargs):
    replicate_all()


@receiver(storage_up)
def sync_on_storage_up(sender, **kwargs):
    pass


# ----------- DJANGO Q HANDLERS -----------
def file_replication_check(file_pk, storage_pk):
    file = File.objects.get(pk=int(file_pk))
    storage = Storage.objects.get(pk=int(storage_pk))
    # Successful replication
    if file.storage.filter(pk=storage.pk).exists():
        logger.info(f'Succ repl check {file.file_path} {storage.ip}')
    # Something went wrong
    # Try to replicate again
    else:
        replicate_file(file)
