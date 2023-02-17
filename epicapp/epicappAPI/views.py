from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status
from django.http import JsonResponse

from .models import Author
from .serializers import AuthorSerializer, PostSerializer

@api_view((['POST']))
def signup(request):
    author_data = request.data
    author = AuthorSerializer(data=request.data)

    if not author.is_valid():
        return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

    author.save()

    return Response(author.data)

@api_view((['POST']))
def signin(request):
    return Response(data="create author") 

@api_view(['GET'])
def get_author(request, id):
    return Response(data="get single author")

@api_view(['GET'])
def get_authors(request):
    return Response(data="get many authors")

@api_view(['POST'])
def create_post(request, author_id):
    # TODO: authorization check
    # TODO: permission check
    post_data = request.data
    post_data["author_id"] = author_id
    post = PostSerializer(data=post_data)
    
    if not post.is_valid():
        return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

    post.save()

    return Response(data=post.data)
