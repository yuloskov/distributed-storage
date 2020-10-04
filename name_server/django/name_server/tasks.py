from django.conf import settings

from logging import log
from django.dispatch import receiver

from .signals import (
    file_saved,
    storage_deleted,
)
from .utils import (
    replicate_all,
    replicate_file,
)

import logging

logger = logging.getLogger(__name__)


@receiver(file_saved)
def replicate_on_file_save(sender, **kwargs):
    file = kwargs['file']
    storage = kwargs['storage']

    if file.storage.count() < settings.NUM_OF_REPLICAS:
        logger.info(f'REPLICATING {file.file_path}')
        replicate_file(file)
    else:
        logger.info(f'ENOUGH COPIES {file.file_path}')

@receiver(storage_deleted)
def replicate_on_storage_delete(sender, **kwargs):
    replicate_all()
