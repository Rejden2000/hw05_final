from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('create/', views.post_create, name='post_create'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success', views.success_view, name='success'),
    path('posts/<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('', views.index, name='index'),
]
