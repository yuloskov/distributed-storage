from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FileViewSet,
    StorageViewSet,
)

import logging

logger = logging.getLogger(__name__)

router = DefaultRouter()
router.register(r'file', FileViewSet, basename='files')
router.register(r'storage', StorageViewSet, basename='storage',)

urlpatterns = [
    path('', include(router.urls)),
]
