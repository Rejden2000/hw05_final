from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from rest_framework import status
import shutil
import tempfile
from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.author = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        cache.clear()

    def test_post_create_form(self):
        """Валидная форма создает запись в БД и
        С помощью sorl-thumbnail выведены иллюстрации к постам:."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Второй тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'NoName'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.latest('id'))
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])

        templates_url_names = {
            '/',
            '/group/test-slug/',
            '/profile/NoName/',
            '/posts/1/',
        }

        for address in templates_url_names:
            with self.subTest():
                response = self.authorized_author.get(address)
                self.assertContains(response, '<img')

    def test_post_edit_forms(self):
        """Валидная форма редактирует запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edit_post_var = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post_var.text, form_data['text'])
        self.assertEqual(edit_post_var.author, self.post.author)

    def test_post_create_form1(self):
        """Проверка отсутствия доступа неавторизированного
        пользователя к БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Третий тестовый текст',
            'group': self.group
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_add_comment_form1(self):
        """Комментировать посты может только авторизованный
        пользователь."""
        comments = self.post.comments.count()
        form_comment = {
            'text': 'Комментарий к посту',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_comment,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments)

    def test_add_comment_form2(self):
        """После успешной отправки комментарий
        появляется на странице поста"""
        comments = self.post.comments.count()
        form_comment = {
            'text': 'Комментарий к посту',
        }
        self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_comment,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments + 1)
