from django.test import TestCase
from rest_framework import status


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
