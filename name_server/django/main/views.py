from rest_framework import (
    viewsets,
    response,
    status,
)
from rest_framework.decorators import action

from django.http import Http404
from django.conf import settings

from .models import File
from .models import Storage

from .serializers import FileSerializer
from .serializers import StorageSerializer

import logging

logger = logging.getLogger(__name__)


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = File.objects.all()

    # Redefine create to add storage if file exists
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_path = serializer.validated_data['file_path']
        file_exist = File.objects.filter(file_path=file_path).count() > 0
        if file_exist:
            file = File.objects.get(file_path=file_path)
            file.storage.add(serializer.validated_data['storage'][0])
        else:
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class StorageViewSet(viewsets.ModelViewSet):
    serializer_class = StorageSerializer
    queryset = Storage.objects.all()

    @action(detail=False, methods=['GET'])
    def available(self, request):
        available_servers = Storage.objects.filter(status='UP')
        serializer = StorageSerializer(available_servers, many=True)
        return response.Response(serializer.data, status.HTTP_200_OK)

    # TODO: add action to get all servers with the file
    @action(detail=False, methods=['GET'])
    def replicate_ip(self, request):
        """
        Get the list of servers on which you can put a replica of a file.
        :param request: Request body.
            Should include parameter file_path - the path of
            the file on the server.
        :return: List of servers.
        """
        if 'file_path' not in request.GET:
            raise Http404

        file_path = request.GET['file_path']
        file = File.objects.get(file_path=file_path)
        file_servers = file.storage.all()
        num_copies = file_servers.count()

        if num_copies < settings.NUM_OF_REPLICAS:
            available_servers = Storage.objects.filter(status='UP')
            no_file_servers = available_servers.difference(file_servers)
            serializer = StorageSerializer(no_file_servers, many=True)
            return response.Response(serializer.data, status.HTTP_200_OK)

        return response.Response([], status.HTTP_200_OK)
