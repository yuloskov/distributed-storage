from django.apps import AppConfig


class NameServerConfig(AppConfig):
    name = 'name_server'

    def ready(self):
        from . import tasks
