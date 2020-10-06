from django.dispatch import Signal

file_saved = Signal(providing_args=['file'])
storage_up = Signal()
storage_down = Signal()
