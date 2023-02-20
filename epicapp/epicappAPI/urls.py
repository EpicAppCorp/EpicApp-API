from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/authenticate/', views.authenticate, name='authenticate'),
    path('auth/logout/', views.logout, name='logout'),

    path('author/details/', views.get_author_details, name='get_author_details'),
    path('author/<str:id>', views.get_author, name='get_author'),
    path('authors/', views.get_authors, name='get_authors'),
    path('authors/<str:author_id>/posts', views.posts, name='posts endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments', views.comments, name="post endpoint"),

    path('authors/<str:id>/inbox', views.inbox, name='inbox'),

    path('authors/<str:author_id>/posts/<str:post_id>/likes', views.post_likes, name="post likes endpoint"),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.comment_likes, name="comments likes endpoint")
]
