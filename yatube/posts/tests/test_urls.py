from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(self.auth)

    def test_homepage(self):
        """Страница и её шаблон доступны любому пользователю."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/unexisting_page/': ''
        }
        for address, template in templates_url_names.items():
            if address == '/posts/1/edit/':
                with self.subTest(address=address):
                    response = self.authorized_client_auth.get(address)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertTemplateUsed(response, template)
            elif address == '/create/':
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertTemplateUsed(response, template)
            elif address == '/unexisting_page/':
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code,
                                     status.HTTP_404_NOT_FOUND)
            else:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertTemplateUsed(response, template)
