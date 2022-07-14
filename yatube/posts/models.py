from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name="Адрес группы")
    description = models.TextField(verbose_name="Описание сообщества")

    class Meta:
        verbose_name = "Список групп"
        verbose_name_plural = "Список групп"

    def __str__(self):
        return self.title


class Post(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.PROTECT, related_name="posts",
                              verbose_name="Название группы")
    text = models.TextField(verbose_name="Текст поста",
                            help_text="Поле для записи поста.")
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name="Дата публикации")
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name='Автор',
    )
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        verbose_name = "Список постов"
        verbose_name_plural = "Список постов"
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(Post, blank=True, null=True,
                             on_delete=models.CASCADE, related_name="comments",
                             verbose_name="Комментируемый пост")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор комментария',
    )
    text = models.TextField(verbose_name="Текст комментария",
                            help_text="Поле для записи комментария.")
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name="Дата комментария")


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Автор комментария',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='Автор комментария',
    )
