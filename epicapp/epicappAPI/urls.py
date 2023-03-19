from django.urls import path
from .views import RegisterView, AuthenticateView, LogoutView, AuthorView, AuthorsView, PostView, PostsView, PostImageView, CommentsView, FollowersView, FollowerView

urlpatterns = [
    # auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/authenticate/', AuthenticateView.as_view(), name='authenticate'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # authors
    path('authors/<str:id>/', AuthorView.as_view(), name='get_author'),
    path('authors/', AuthorsView.as_view(), name='get_authors'),

    # posts
    path('authors/<str:author_id>/posts/',
         PostsView.as_view(), name='posts_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/',
         PostView.as_view(), name='post_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/image/',
         PostImageView.as_view(), name='post_image_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments',
         CommentsView.as_view(), name="comments endpoint"),
    #     path('authors/<str:author_id>/posts/<str:post_id>/likes',
    #          views.post_likes, name="post likes endpoint"),
    #     path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes',
    #          views.comment_likes, name="comments likes endpoint"),

    #     # likes
    #     path('authors/<str:id>/liked', views.liked,
    #          name="liked items (comments and posts)"),

    #     # inbox
    #     path('authors/<str:id>/inbox', views.inbox, name='inbox'),

    #     # followers
    path('authors/<str:author_id>/followers/',
         FollowersView.as_view(), name="get followers endpoint"),
    path('authors/<str:author_id>/followers/<path:foreign_author_id>',
         FollowerView.as_view(), name="following endpoint"),

]
