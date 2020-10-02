from rest_framework import status
from rest_framework.test import APITestCase

from .models import Storage


class APITest(APITestCase):
    ip1 = '10.21.15.1'
    ip2 = '10.21.15.2'
    ip3 = '10.21.15.3'
    ip4 = '10.21.15.4'
    ip5 = '10.21.15.5'

    url_file = '/api/file/'

    def get_file_id(self, file_path):
        response = self.client.get('/api/file/id/', {'file_path': file_path})
        return response.data['id']

    def get_storage_id(self, ip):
        response = self.client.get('/api/storage/id/', data={'ip': ip})
        return response.data['id']

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

        st1_id = self.get_storage_id(self.ip1)
        st2_id = self.get_storage_id(self.ip2)
        self.client.post(
            self.url_file,
            {'file_path': '/a/b', 'storage': st1_id},
        )
        self.client.post(
            self.url_file,
            {'file_path': '/a/b', 'storage': st2_id},
        )
        self.client.post(
            self.url_file,
            {'file_path': '/a/c', 'storage': st1_id},
        )
        self.client.post(
            self.url_file,
            {'file_path': '/a/d', 'storage': st2_id},
        )

        # TEST /a/b
        file_id = self.get_file_id('/a/b')
        response = self.client.get(f'/api/file/{file_id}/replicate_ip/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # TEST /a/c
        file_id = self.get_file_id('/a/c')
        response = self.client.get(f'/api/file/{file_id}/replicate_ip/')
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
        file_id = self.get_file_id('/a/d')
        response = self.client.get(f'/api/file/{file_id}/replicate_ip/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            list(map(dict, list(response.data))), [
                {'ip': self.ip1},
                {'ip': self.ip3},
                {'ip': self.ip4},
                {'ip': self.ip5},
            ],
        )

    def test_delete(self):
        Storage.objects.create(ip=self.ip1)
        Storage.objects.create(ip=self.ip2)
        Storage.objects.create(ip=self.ip3)
        Storage.objects.create(ip=self.ip4)
        Storage.objects.create(ip=self.ip5)

        st1_id = self.get_storage_id(self.ip1)
        st2_id = self.get_storage_id(self.ip2)

        self.client.post(
            self.url_file,
            {'file_path': '/a/b', 'storage': st1_id},
        )
        self.client.post(
            self.url_file,
            {'file_path': '/a/b', 'storage': st2_id},
        )

        file_id = self.get_file_id('/a/b')
        self.client.delete(f'{self.url_file}{file_id}/')

        response = self.client.get(self.url_file)

        self.assertEqual(response.data, [])
