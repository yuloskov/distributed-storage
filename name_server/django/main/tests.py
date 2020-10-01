from rest_framework import status
from rest_framework.test import APITestCase

from .models import Storage, File


class APITest(APITestCase):
    ip1 = '10.21.15.1'
    ip2 = '10.21.15.2'
    ip3 = '10.21.15.3'
    ip4 = '10.21.15.4'
    ip5 = '10.21.15.5'

    def test_available(self):
        Storage.objects.create(ip=self.ip1, status='DN')
        Storage.objects.create(ip=self.ip2, status='UP')
        Storage.objects.create(ip=self.ip3, status='UP')
        Storage.objects.create(ip=self.ip4, status='UP')
        Storage.objects.create(ip=self.ip5, status='PD')

        response = self.client.get('/api/storage/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {'ip': self.ip2},
            {'ip': self.ip3},
            {'ip': self.ip4},
        ])

    def test_replicas(self):
        Storage.objects.create(ip=self.ip1)
        Storage.objects.create(ip=self.ip2)
        Storage.objects.create(ip=self.ip3)
        Storage.objects.create(ip=self.ip4)
        Storage.objects.create(ip=self.ip5)

        file1 = File.objects.create(file_path='/a/b')
        file1.storage.add(self.ip1)
        file1.storage.add(self.ip2)

        File.objects.create(file_path='/a/c').storage.add(self.ip1)
        File.objects.create(file_path='/a/d').storage.add(self.ip2)

        # TEST /a/b
        response = self.client.get(
            '/api/storage/replicate_ip/',
            data={'file_path': '/a/b'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # TEST /a/c
        response = self.client.get(
            '/api/storage/replicate_ip/',
            data={'file_path': '/a/c'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            list(map(dict, list(response.data))), [
                {'ip': self.ip2},
                {'ip': self.ip3},
                {'ip': self.ip4},
                {'ip': self.ip5},
            ],
        )

        # TEST /a/d
        response = self.client.get(
            '/api/storage/replicate_ip/',
            data={'file_path': '/a/d'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            list(map(dict, list(response.data))), [
                {'ip': self.ip1},
                {'ip': self.ip3},
                {'ip': self.ip4},
                {'ip': self.ip5},
            ],
        )
