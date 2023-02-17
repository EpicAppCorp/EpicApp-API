from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/authenticate/', views.authenticate, name='authenticate'),
    path('auth/logout/', views.logout, name='logout'),

    path('author/details/', views.get_author_details, name='get_author_details'),
    path('author/<str:id>', views.get_author, name='get_author'),
    path('authors/', views.get_authors, name='get_authors'),
]
