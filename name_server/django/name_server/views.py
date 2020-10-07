from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse

from .models import (
    File,
    Storage,
)
from .signals import file_saved

import os
import random
import logging
import requests

logger = logging.getLogger(__name__)


def available(request):
    available_servers = Storage.objects.filter(status='UP')

    if len(available_servers) == 0:
        return HttpResponse(status=404)

    available_server = random.choice(available_servers)

    public_ip = available_server.public_ip
    return JsonResponse({'ip': public_ip}, status=200)


def create_storage(request):
    private_ip = request.META.get('REMOTE_ADDR')
    public_ip = os.environ['PUBLIC_IP']

    Storage.objects.get_or_create(
        public_ip=public_ip,
        private_ip=private_ip
    )
    return HttpResponse(status=200)


def file_view(request):
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        file_hash = request.POST.get('file_hash')
        file_size = request.POST.get('file_size')
        private_ip = request.META.get('REMOTE_ADDR')

        storage = Storage.objects.get(private_ip=private_ip)
        file = File.objects.filter(file_path=file_path).first()

        if file is None:
            file = File.objects.create(
                file_path=file_path,
                hash=file_hash,
                size=file_size,
            )
        elif file.hash != file_hash:
            file.delete()
            file = File.objects.create(
                file_path=file_path,
                hash=file_hash,
                size=file_size,
            )
        file.storage.add(storage)

        # Send replication signal
        logger.info('Sending SIGNAL on file save')
        file_saved.send(sender=None, file=file)

        return HttpResponse(status=200)
    elif request.method == 'DELETE':
        file_path = request.GET.get('file_path')

        file = get_object_or_404(File, file_path=file_path)
        servers = file.storage.filter(status='UP')
        for server in servers:
            url = f'http://{server.private_ip}:{settings.STORAGE_SERVER_PORT}/file'
            requests.delete(url, params={'file_path': file_path})
        file.delete()

        return HttpResponse(status=200)
    elif request.method == 'GET':
        file_path = request.GET.get('file_path')

        file = get_object_or_404(File, file_path=file_path)
        storage = random.choice(file.storage.filter(status='UP'))

        return JsonResponse({'ip': storage.public_ip})

    return HttpResponse(status=400)


def list_files(request):
    path = request.GET.get('dir_path')
    res = {file.file_path: {'hash': file.hash, 'file_size': file.size, 'modified': file.last_modified}
           for file in File.objects.filter(file_path__startswith=path)}
    return JsonResponse(res, status=200)


def restore_storages(request):
    if not request.user.is_superuser:
        return HttpResponse(status=403)

    if File.objects.count() > 0:
        return JsonResponse({'message': 'DB not empty'}, status=200)

    storage_dumps = [
        (storage, requests.get(f'http://{storage.private_ip}:{settings.STORAGE_SERVER_PORT}/dump_tree').json())
        for storage in Storage.objects.all()
    ]

    files = {}
    for storage, storage_files in storage_dumps:
        for p in storage_files:
            file = storage_files[p]
            if p not in files:
                files[p] = {}
            hash = file['hash']
            if hash not in files[p]:
                files[p][hash] = (file['size'], [])
            files[p][hash][1].append(storage)

    for p in files:
        best_hash = None
        best_size = None
        for hash in files[p]:
            size, storage_list = files[p][hash]
            enough_replicas = len(storage_list) >= settings.NUM_OF_REPLICAS
            if enough_replicas and (best_hash is None or len(storage_list) > len(files[p][best_hash][1])):
                best_hash = hash
                best_size = size
        if best_hash is not None:
            file = File.objects.create(file_path=p, hash=best_hash, size=best_size)
            file.storage.set(files[p][best_hash][1])
    return JsonResponse({'message': 'OK', 'num_files': File.objects.count()}, status=200)
