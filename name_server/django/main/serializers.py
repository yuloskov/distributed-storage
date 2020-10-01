from rest_framework import serializers

from .models import File
from .models import Storage


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = [
            'ip',
        ]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'file_path',
            'storage',
        ]
