from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.urls import path

from .views import *


api = [
    path('storage/available/', available),
    path('storage/', create_storage),
    path('file/', file_view),
    path('ls/', list_files),
    path('restore/', restore_storages)
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
