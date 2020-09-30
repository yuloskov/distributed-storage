from django.db import models

import uuid


class Storage(models.Model):
    ip = models.GenericIPAddressField(
        primary_key=True,
    )


class File(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
    )
    storage = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
