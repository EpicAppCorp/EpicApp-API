from django.urls import re_path, path
from . import views

urlpatterns = [
    # auth
    re_path(r'auth/register/?$', views.RegisterView.as_view(), name='register'),
    re_path(r'auth/authenticate/?$',
            views.AuthenticateView.as_view(), name='authenticate'),
    re_path(r'auth/logout/?$', views.LogoutView.as_view(), name='logout'),
    re_path(r'auth/details/?$', views.AuthorDetails.as_view(),
            name='get_author_local'),

    # getting all authors from all servers
    re_path(r'friends\/?$', views.FriendsView.as_view(), name='get_friends'),


    re_path(r'^authors\/(?P<id>.+?)\/inbox\/?$',
            views.InboxView.as_view(), name='inbox'),
    re_path(r'authors\/(?P<id>.+?)\/liked\/?$', views.LikedView.as_view(),
            name="liked items (comments and posts)"),
    re_path(r'authors\/(?P<author_id>.+?)\/posts\/(?P<post_id>.+?)\/image\/?$',
            views.PostImageView.as_view(), name='post_image_endpoint'),

    re_path(r'authors/(?P<author_id>.+?)\/posts\/(?P<post_id>.+?)\/comments\/(?P<comment_id>.+?)\/likes\/?$',
            views.CommentLikesView.as_view(), name="comments likes endpoint"),
    re_path(r'authors/(?P<author_id>.+?)\/posts\/(?P<post_id>.+?)\/comments\/?$',
            views.CommentsView.as_view(), name="comments endpoint"),
    #     missing like for single post
    re_path(r'authors/(?P<author_id>.+?)\/posts\/(?P<post_id>.+?)\/likes\/?$',
            views.LikesView.as_view(), name="post likes endpoint"),
    re_path(r'authors\/(?P<author_id>.+?)\/posts\/(?P<post_id>.+?)\/?$',
            views.PostView.as_view(), name='post_endpoint'),
    re_path(r'authors\/(?P<author_id>.+?)\/posts\/?$',
            views.PostsView.as_view(), name='posts_endpoint'),

    # followers
    path('authors/<str:author_id>/followers/<path:foreign_author_id>',
         views.FollowerView.as_view(), name="following endpoint"),
    re_path(r'authors\/(?P<author_id>.+?)\/followers\/?$',
            views.FollowersView.as_view(), name="get followers endpoint"),
    # authors
    re_path(r'authors\/(?P<id>.+?)\/?$',
            views.AuthorView.as_view(), name='get_author'),
    re_path(r'authors\/?$', views.AuthorsView.as_view(), name='get_authors'),

]
