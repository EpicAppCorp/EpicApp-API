from django.urls import path
from . import views

urlpatterns = [
    path('author/', views.create_author, name='create_author'),
    path('author/<str:id>', views.get_author, name='get_author'),
    path('authors/', views.get_authors, name='get_authors'),
]