from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = (
            "Группа, к которой будет относиться пост")

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': (
                    'Напишите что нибудь и пусть весь мир Вас услышт!!')}),
        }


class ContactForm(forms.Form):
    subject = forms.CharField(
        label='Тема', required=True,
        widget=forms.TextInput(
            attrs={'placeholder': (
                'Напишите тему обращеня')})
    )
    message = forms.CharField(
        label='Сообщение', required=True,
        widget=forms.Textarea(
            attrs={'placeholder': (
                'Напишите и мы обязательно Вам ответим')})
    )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': (
                    'Напишите что думаете о данном посте...')}),
        }
