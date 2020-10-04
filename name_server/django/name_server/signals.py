from django.dispatch import Signal

file_saved = Signal(providing_args=['file', 'storage'])
storage_up = Signal()
storage_down = Signal()
