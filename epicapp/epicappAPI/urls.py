from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('author/<str:id>', views.get_author, name='get_author'),
    path('authors/', views.get_authors, name='get_authors'),

    # post paths
    path('authors/<str:author_id>/posts/', views.create_post, name='create_post')
]