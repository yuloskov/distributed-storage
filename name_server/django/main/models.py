from django.db import models

STATUS_CHOICES = [
    ('UP', 'Server is up'),
    ('DN', 'Server is down'),
    ('PD', 'Server is doing some task'),
]


class Storage(models.Model):
    ip = models.GenericIPAddressField(
        unique=True
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default='UP',
    )


class File(models.Model):
    file_path = models.CharField(
        max_length=1000,
    )
    storage = models.ManyToManyField(
        Storage,
    )
