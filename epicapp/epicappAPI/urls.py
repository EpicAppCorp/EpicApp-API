from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/authenticate/', views.AuthenticateView.as_view(), name='authenticate'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/details/', views.AuthorDetails.as_view(), name='get_author_local'),

    # authors
    path('authors/<str:id>/', views.AuthorView.as_view(), name='get_author'),
    path('authors/', views.AuthorsView.as_view(), name='get_authors'),

    # getting all authors from all servers
    path('friends/', views.FriendsView.as_view(), name='get_friends'),

    # posts
    path('authors/<str:author_id>/posts/',
         views.PostsView.as_view(), name='posts_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/',
         views.PostView.as_view(), name='post_endpoint'),
    path('authors/<str:author_id>/repost/',
         views.RepostView.as_view(), name='repost_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/image/',
         views.PostImageView.as_view(), name='post_image_endpoint'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/',
         views.CommentsView.as_view(), name="comments endpoint"),
    path('authors/<str:author_id>/posts/<str:post_id>/likes/',
         views.LikesView.as_view(), name="post likes endpoint"),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes/',
         views.CommentLikesView.as_view(), name="comments likes endpoint"),
    path('authors/<str:id>/liked/', views.LikedView.as_view(),
         name="liked items (comments and posts)"),

    # inbox
    path('authors/<str:id>/inbox/', views.InboxView.as_view(), name='inbox'),

    # followers
    path('authors/<str:author_id>/followers/',
         views.FollowersView.as_view(), name="get followers endpoint"),
    path('authors/<str:author_id>/followers/<path:foreign_author_id>',
         views.FollowerView.as_view(), name="following endpoint"),

]
