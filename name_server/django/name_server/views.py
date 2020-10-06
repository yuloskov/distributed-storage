from logging import log
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import (
    File,
    Storage,
)
from .signals import file_saved

from django.http import HttpResponse, JsonResponse
import random
import logging
import requests

logger = logging.getLogger(__name__)


def available(request):
    available_servers = Storage.objects.filter(status='UP')

    if len(available_servers) == 0:
        return HttpResponse(status=404)

    available_server = random.choice(available_servers)

    ip = available_server.ip
    return JsonResponse({'ip': ip}, status=200)


def create_storage(request):
    server_ip = request.META.get('REMOTE_ADDR')
    Storage.objects.get_or_create(ip=server_ip)
    return HttpResponse(status=200)


def file_view(request):
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        file_hash = request.POST.get('file_hash')
        server_ip = request.META.get('REMOTE_ADDR')

        storage = Storage.objects.get(ip=server_ip)
        file = File.objects.filter(file_path=file_path).first()

        if file is None:
            file = File.objects.create(file_path=file_path,
                                       hash=file_hash)
        elif file.hash != file_hash:
            file.delete()
            file = File.objects.create(file_path=file_path,
                                       hash=file_hash)
        file.storage.add(storage)

        # Send replication signal
        logger.info('Sending SIGNAL on file save')
        file_saved.send(sender=None, file=file, storage=storage)

        return HttpResponse(status=200)
    elif request.method == 'DELETE':
        file_path = request.GET.get('file_path')

        file = get_object_or_404(File, file_path=file_path)
        servers = file.storage.filter(status='UP')
        for server in servers:
            url = f'http://{server.ip}:{settings.STORAGE_SERVER_PORT}/file'
            requests.delete(url, params={'file_path': file_path})
        file.delete()

        return HttpResponse(status=200)
    elif request.method == 'GET':
        file_path = request.GET.get('file_path')

        file = get_object_or_404(File, file_path=file_path)
        storage = random.choice(file.storage.filter(status='UP'))

        return JsonResponse({"ip": storage.ip})

    return HttpResponse(status=400)


def list_files(request):
    path = request.GET.get('dir_path')
    res = {file.file_path: {"hash": file.hash} for file in File.objects.filter(file_path__startswith=path)}
    return JsonResponse(res, status=200)
