from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='123456789101112131415 Тестовая пост',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))

    def test_title_label(self):
        """verbose_name поля group совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Название группы')

    def test_title_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_title_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        text = post._meta.get_field('text').help_text
        self.assertEqual(text, 'Поле для записи поста.')

    def test_title_label(self):
        """verbose_name поля title (Group) совпадает с ожидаемым."""
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')
