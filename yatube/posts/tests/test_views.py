from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        index_author_0 = first_object.author
        index_text_0 = first_object.text
        self.assertEqual(str(index_author_0), 'auth')
        self.assertEqual(index_text_0, 'Тестовая пост')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        group_list_author_0 = first_object.author
        group_list_text_0 = first_object.text
        group_list_title_1 = second_object.title
        group_list_slug_1 = second_object.slug
        self.assertEqual(str(group_list_author_0), 'auth')
        self.assertEqual(group_list_text_0, 'Тестовая пост')
        self.assertEqual(group_list_title_1, 'Тестовая группа')
        self.assertEqual(group_list_slug_1, 'test-slug')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['author']
        group_list_author_0 = first_object.author
        group_list_text_0 = first_object.text
        group_list_title_1 = second_object.username
        self.assertEqual(str(group_list_author_0), 'auth')
        self.assertEqual(group_list_text_0, 'Тестовая пост')
        self.assertEqual(group_list_title_1, 'auth')

    def test_prost_detail_page_show_correct_context(self):
        """Шаблон prost_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        self.assertEqual(response.context['post'].text, 'Тестовая пост')

    def test_prost_create_list_page_show_correct_context(self):
        """Шаблон prost_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_prost_create_page_show_correct_context(self):
        """Шаблон prost_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_1 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_2 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_3 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_4 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_5 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_6 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_7 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_8 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_9 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_10 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_11 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_12 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )
        cls.post_13 = Post.objects.create(
            group=cls.group,
            text='Тестовая пост',
            pub_date='1854-03-14 00:00:00',
            author=cls.auth
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth)

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице index равно 10."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        """Проверка: количество постов на второй странице index равно 3."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_page_contains_three_records(self):
        """Проверка: количество постов
        на второй странице group_list равно 3."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_contains_three_records(self):
        """Проверка: количество постов на второй странице profile равно 3."""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response_before = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            text='test_new_post',
            author=self.auth,
        )
        response_after = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_before.content, response_after.content)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_before.content, response.content)

    def test_auth_follow(self):
        """ Авторизованный пользователь может подписываться на других
            пользователей и удалять их из подписок.
        """
        following = User.objects.create(username='following')
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': following}))
        self.assertIs(
            Follow.objects.filter(user=self.auth, author=following).exists(),
            True
        )

        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           kwargs={'username': following}))
        self.assertIs(
            Follow.objects.filter(user=self.auth, author=following).exists(),
            False
        )

    def test_new_post(self):
        """ Новая запись пользователя появляется в ленте тех, кто на него
            подписан и не появляется в ленте тех, кто не подписан на него.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.auth, author=following)
        post = Post.objects.create(author=following, text='Тестовая коммент')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page'].object_list)

        self.authorized_client.logout()
        User.objects.create_user(
            username='user_temp',
            password='pass'
        )
        self.authorized_client.login(username='user_temp', password='pass')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page'].object_list)
