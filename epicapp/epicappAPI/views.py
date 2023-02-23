import jwt
import uuid
import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException, NotFound
from rest_framework import serializers, status
from django.http import JsonResponse

from .models import Author, Post, Comment, PostLike, CommentLike, Inbox
from .config import HOST
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer, InboxSerializer


@api_view((['POST']))
def register(request):
    if request.method == 'POST':
        author = AuthorSerializer(data=request.data)

        if not author.is_valid():
            return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

        author.save()

        return Response(author.data)


@api_view((['POST']))
def authenticate(request):
    if request.method == 'POST':
        # get first author with username
        author = Author.objects.filter(
            displayName=request.data["displayName"]).first()

        # no user with that display name
        if author is None:
            return Response(data="Author not found!", status=status.HTTP_401_UNAUTHORIZED)

        # if hash passwords aren't the same
        if not author.check_password(request.data["password"]):
            return Response(data="Invalid credentials!", status=status.HTTP_401_UNAUTHORIZED)

        # create token with 60 min expiry
        token = jwt.encode(
            {
                'id': AuthorSerializer(author).data['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }, "SECRET_NOT_USING_ENV_CAUSE_WHO_CARES", algorithm='HS256')

        # return an http only cookie, but if needed to make it easier, we can not do http only cookies so JS can use it.
        response = Response(data="Login successful!",
                            status=status.HTTP_200_OK)
        response.set_cookie(key='token', value=token, httponly=True)
        return response


@api_view((['POST']))
def logout(request):
    if request.method == 'POST':
        response = Response(data="Logout successful!",
                            status=status.HTTP_200_OK)
        response.delete_cookie('token')
        return response


@api_view(['GET'])
def get_author_details(request):
    if request.method == 'GET':
        token = request.COOKIES.get('token')

        if not token:
            return Response(data="Unauthenticated!", status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(
                token, 'SECRET_NOT_USING_ENV_CAUSE_WHO_CARES', algorithms=['HS256'])
            print(payload)
            author = Author.objects.filter(id=payload['id']).first()
            return Response(data=AuthorSerializer(author).data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response(data="Token expired!", status=status.HTTP_401_UNAUTHORIZED)


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
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 5))

            author = Author.objects.get(id=author_id)
            offset = (page - 1) * size
            posts = Post.objects.filter(author_id=author_id)[offset:offset+size]
            serialized_posts = PostSerializer(posts, many=True)
            return Response(data=serialized_posts.data)
        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', 'GET', 'DELETE', 'PUT'])
def post(request, author_id, post_id):
    # TODO: authorization check
    # TODO: permission check

    if request.method == 'PUT':
        post_data = request.data
        post_data["id"] = post_id
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
            post_data["id"] = post_id
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

@api_view(['POST', 'GET'])
def comments(request, author_id, post_id):
    # TODO: authorization check
    # TODO: permission check
    
    if request.method == 'GET':
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 5))

            author = Author.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)

            offset = (page - 1) * size
            comments = Comment.objects.filter(post_id=post_id)[offset:offset+size]
            serialized_comments = CommentSerializer(comments, many=True)

            data = {
                "type": "comments",
                "page": page,
                "size": size,
                "post": f"{HOST}/authors/{author_id}/posts/{post_id}",
                "id": f"{HOST}/authors/{author_id}/posts/{post_id}/comments",
                "comments": serialized_comments.data
            }

            return Response(data=data)

        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response(data=f"Post with id: {post_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'POST':
        comment_data = request.data
        comment_data["post_id"] = post_id
        comment_data["author_id"] = author_id
        comment = CommentSerializer(data=comment_data)

        if not comment.is_valid():
            return Response(data=comment.errors, status=status.HTTP_400_BAD_REQUEST)

        comment.save()

        return Response(data=comment.data)


@api_view(['POST', 'GET'])
def inbox(request, id):
    if request.method == 'POST':
        data = request.data
        type = data["type"]

        if type == "Like":
            data['author_id'] = id
            url_components = data['object'].split('/')
            object_id = url_components[-1]

            if url_components[-2] == "posts":
                try:
                    Post.objects.get(id=object_id)
                except Post.DoesNotExist:
                    return Response(data="Post does not exist", status=status.HTTP_400_BAD_REQUEST)

                data['post_id'] = object_id
                serialized_like = PostLikeSerializer(data=data)

                if not serialized_like.is_valid():
                    return Response(data="something went wrong", status=status.HTTP_400_BAD_REQUEST)

                serialized_like.save()

                inbox_item = Inbox(content_object=serialized_like.instance, author_id=id)
                inbox_item.save()

                return Response(data=serialized_like.data)

            elif url_components[-2] == "comments":
                try:
                    comment = Comment.objects.get(id=object_id)
                except Post.DoesNotExist:
                    return Response(data="Post does not exist", status=status.HTTP_400_BAD_REQUEST)
                except Comment.DoesNotExist:
                    return Response(data="Comment does not exist", status=status.HTTP_400_BAD_REQUEST)

                data['comment_id'] = object_id
                data['post_id'] = url_components[-3]
                serialized_like = CommentLikeSerializer(data=data)

                if not serialized_like.is_valid():
                    return Response(data="something went wrong", status=status.HTTP_400_BAD_REQUEST)

                serialized_like.save()

                inbox_item = Inbox(content_object=serialized_like.instance, author_id=id)
                inbox_item.save()

                comment_data = serialized_like.data

                return Response(data=comment_data)

            else:
                return Response("Wtf you tryna do", status=status.HTTP_400_BAD_REQUEST)

        elif type == "post":
            return Response("not implemented")
        elif type == "comment":
            return Response("not implemented")
        elif type == "Follow":
            return Response("not implemented")
    elif request.method == 'GET':
        inbox_items = Inbox.objects.filter(author_id=id)
        serialized_inbox_items = InboxSerializer(inbox_items, many=True)
        return Response(serialized_inbox_items.data)

@api_view(['GET'])
def post_likes(request, author_id, post_id):
    post_likes = PostLike.objects.filter(post_id=post_id)
    serialized_post_like = PostLikeSerializer(post_likes, many=True)
    return Response(data=serialized_post_like.data)

@api_view(['GET'])
def comment_likes(request, author_id, post_id, comment_id):
    comment_likes = CommentLike.objects.filter(comment_id=comment_id)
    serialized_comment_like = CommentLikeSerializer(comment_likes, many=True)
    return Response(data=serialized_comment_like.data)

@api_view(['GET'])
def liked(request, id):
    liked_comments = CommentLike.objects.filter(author_id=id)
    liked_posts = PostLike.objects.filter(author_id=id)

    serialized_liked_comments = CommentLikeSerializer(liked_comments, many=True)
    serialized_liked_posts = PostLikeSerializer(liked_posts, many=True)

    data = {
        "type": "liked",
        "items": serialized_liked_posts.data + serialized_liked_comments.data # TODO: find better way to combine
    }

    return Response(data)
