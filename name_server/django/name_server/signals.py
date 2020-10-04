from django.dispatch import Signal

file_saved = Signal(providing_args=['file', 'storage'])
storage_deleted = Signal()
