from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from posts.forms import PostForm, ContactForm, CommentForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Group, Follow

User = get_user_model()


def index(request):
    keyword = request.GET.get("search", None)
    if keyword:
        post_list = Post.objects.filter(text__contains=keyword)
        paginator = Paginator(post_list, 10)
    else:
        post_list = Post.objects.all()
        paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'keyword': keyword,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count = post.author.posts.select_related('author').all().count()
    form_comment = CommentForm()
    comments = post.comments.select_related('post').all()
    context = {
        'post': post,
        'count': count,
        'form_comment': form_comment,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author').all()
    count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user = request.user
    following = user.is_authenticated and author.following.exists()
    context = {
        'author': author,
        'count': count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.author = request.user
                obj.save()
                return redirect('posts:profile', obj.author)
            except ValueError:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = PostForm()
    context = {
        'form': form,
        'title': 'Добавить запись',
        'button': 'Добавить'
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('users:logged_out')
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            try:
                form.save()
                return redirect('posts:post_detail', post_id)
            except ValueError:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = PostForm(instance=post)
    context = {
        'post_id': post_id,
        'form': form,
        'title': 'Редактировать запись',
        'button': 'Сохранить'
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        return redirect('posts:profile', request.user)
    else:
        return redirect('users:logged_out')


@login_required
def contact_view(request):
    if request.method == 'GET':
        form = ContactForm()
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = request.user.email
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email,
                          ['sterlikov.1997.97@gmail.com'])
                return redirect('posts:success')
            except BadHeaderError:
                form.add_error(None, 'Ошибка отправки письма')
    else:
        return HttpResponse('Неверный запрос.')
    return render(request, "contact/email.html", {'form': form})


def success_view(request):
    return render(request, "contact/success.html")


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('posts:post_detail', post_id=post_id)
    form = CommentForm()
    return render(
        request,
        'posts/add_comment.html',
        {
            'post': post,
            'form': form
        }
    )


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    post_list = Post.objects.filter(author__id__in=authors)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
