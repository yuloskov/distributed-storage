from django.urls import path

from .views import *

import logging

logger = logging.getLogger(__name__)

urlpatterns = [
    path('storage/available/', available),
    path('storage/', create_storage),
    path('file/', file_view),
    path('ls/', list_files)
]
