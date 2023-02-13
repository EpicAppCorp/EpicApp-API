from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException, NotFound
from rest_framework import serializers, status
from django.http import JsonResponse

from .models import Author, Post
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

@api_view(['POST', 'GET'])
def posts(request, author_id):
    # TODO: authorization check
    # TODO: permission check

    if request.method == 'POST':
        post_data = request.data
        post_data["author_id"] = author_id
        post = PostSerializer(data=post_data)
        
        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        return Response(data=post.data)

    elif request.method == 'GET':
        posts = Post.objects.filter(author_id=author_id)
        serialized_posts = PostSerializer(posts, many=True)
        return Response(data=serialized_posts.data)

@api_view(['POST', 'GET', 'DELETE', 'PUT'])
def post(request, author_id, post_id):
    # TODO: authorization check
    # TODO: permission check

    if request.method == 'PUT':
        post_data = request.data
        post_data["author_id"] = author_id
        post = PostSerializer(data=post_data)
        
        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        return Response(data=post.data) 

    elif request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            serialized_post = PostSerializer(post)
            return Response(data=serialized_post.data)
        except Post.DoesNotExist as e:
            return Response(data=e, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            post_data = request.data
            updated_post = PostSerializer(instance=post, data=post_data, partial=True)

            if not updated_post.is_valid():
                return Response(data=updated_post.errors, status=status.HTTP_400_BAD_REQUEST)

            updated_post.save()

            return Response(data=updated_post.data)
        except Post.DoesNotExist as e:
            return Response(data=e, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        affected_rows = Post.objects.filter(id=post_id).delete()
        if affected_rows[0] == 0:
            return Response(data=f"could not delete post with id \'{post_id}\'", status=status.HTTP_404_NOT_FOUND)
        return Response(data=affected_rows[0])
