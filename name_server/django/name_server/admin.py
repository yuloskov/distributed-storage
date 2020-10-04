from django.contrib import admin
from .models import *


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = (
        "ip",
        "status",
        "num_of_files",
    )

    readonly_fields = (
        "ip",
        "status",
        "files_",
    )

    def files_(self, obj):
        return ', '.join([file.file_path for file in obj.files.all()])

    def num_of_files(self, obj):
        return obj.files.count()


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "file_path",
        "hash",
        "num_of_replicas",
    )

    readonly_fields = (
        "file_path",
        "hash",
        "storage",
    )

    def num_of_replicas(self, obj):
        return obj.storage.count()
