from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('auth/register/', views.register, name='register'),
    path('auth/authenticate/', views.authenticate, name='authenticate'),
    path('auth/logout/', views.logout, name='logout'),

    # authors
    path('author/details/', views.get_author_details, name='get_author_details'),
    path('author/<str:id>', views.get_author, name='get_author'),
    path('authors/', views.get_authors, name='get_authors'),

    # posts
    path('authors/<str:author_id>/posts', views.posts, name='posts endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments',
         views.comments, name="post endpoint"),
    path('authors/<str:author_id>/posts/<str:post_id>/likes',
         views.post_likes, name="post likes endpoint"),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes',
         views.comment_likes, name="comments likes endpoint"),

    # likes
    path('authors/<str:id>/liked', views.liked,
         name="liked items (comments and posts)"),

    # inbox
    path('authors/<str:id>/inbox', views.inbox, name='inbox'),

    # followers
    path('authors/<str:author_id>/followers/',
         views.followers, name="get followers endpoint"),
    path('authors/<str:author_id>/followers/<str:foreign_author_id>',
         views.author_followers, name="following endpoint"),

]
