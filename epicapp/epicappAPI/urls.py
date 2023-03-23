from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/authenticate/', views.AuthenticateView.as_view(), name='authenticate'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/details/', views.AuthorDetails.as_view(), name='get_author_local'),

    # authors
    path('authors/<path:id>/', views.AuthorView.as_view(), name='get_author'),
    path('authors/', views.AuthorsView.as_view(), name='get_authors'),

    # posts
    path('authors/<path:author_id>/posts/',
         views.PostsView.as_view(), name='posts_endpoint'),
    path('authors/<path:author_id>/posts/<path:post_id>/',
         views.PostView.as_view(), name='post_endpoint'),
    path('authors/<path:author_id>/posts/<path:post_id>/image/',
         views.PostImageView.as_view(), name='post_image_endpoint'),
    path('authors/<path:author_id>/posts/<path:post_id>/comments',
         views.CommentsView.as_view(), name="comments endpoint"),
    path('authors/<path:author_id>/posts/<path:post_id>/likes/',
         views.LikesView.as_view(), name="post likes endpoint"),
    path('authors/<path:author_id>/posts/<path:post_id>/comments/<path:comment_id>/likes',
         views.CommentLikesView.as_view(), name="comments likes endpoint"),
    path('authors/<path:id>/liked', views.LikedView.as_view(),
         name="liked items (comments and posts)"),

    # inbox
    path('authors/<path:id>/inbox', views.InboxView.as_view(), name='inbox'),

    # followers
    path('authors/<path:author_id>/followers/',
         views.FollowersView.as_view(), name="get followers endpoint"),
    path('authors/<path:author_id>/followers/<path:foreign_author_id>',
         views.FollowerView.as_view(), name="following endpoint"),

]
