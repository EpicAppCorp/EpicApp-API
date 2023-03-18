import jwt
import uuid
import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException, NotFound
from rest_framework import serializers, status
from django.http import JsonResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Author, Post, Comment, PostLike, CommentLike, Inbox, Follower
from .config import HOST
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer, InboxSerializer, FollowerSerializer


@swagger_auto_schema(method='post', operation_description="Signup", request_body=AuthorSerializer)
@api_view((['POST']))
def register(request):
    if request.method == 'POST':

        author = AuthorSerializer(data=request.data)

        if not author.is_valid():
            return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

        author.save()

        return Response(author.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='post', operation_description="Login")
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
        response = Response(data=AuthorSerializer(author).data,
                            status=status.HTTP_200_OK)
        response.set_cookie(key='access', value=token,
                            secure=False, samesite='Strict')
        return response


@swagger_auto_schema(method='post', operation_description="logout")
@api_view((['POST']))
def logout(request):
    if request.method == 'POST':
        response = Response(data="Logout successful!",
                            status=status.HTTP_200_OK)
        response.delete_cookie('access')
        return response


@swagger_auto_schema(method='get', operation_description="Get details of author", responses={200: AuthorSerializer})
@api_view(['GET'])
def get_author_details(request):
    if request.method == 'GET':
        token = request.COOKIES.get('access')

        if not token:
            return Response(data="Unauthenticated!", status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(
                token, 'SECRET_NOT_USING_ENV_CAUSE_WHO_CARES', algorithms=['HS256'])

            author = Author.objects.filter(id=payload['id']).first()
            return Response(data=AuthorSerializer(author).data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response(data="Token expired!", status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_author(request, id):
    if request.method == 'GET':
        author = Author.objects.filter(id=id).first()
        return Response(data=AuthorSerializer(author).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_authors(request):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))

        offset = (page - 1) * size
        authors = Author.objects.all()[
            offset:offset+size]
        serialized_authors = AuthorSerializer(authors, many=True)
        return Response(data=serialized_authors.data)


@swagger_auto_schema(method='get', operation_description="Get a list of posts (paginated)", responses={200: PostSerializer(many=True)})
@swagger_auto_schema(method='post', operation_description="Create a post", request_body=PostSerializer, responses={200: PostSerializer})
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
            posts = Post.objects.filter(author_id=author_id)[
                offset:offset+size]
            serialized_posts = PostSerializer(posts, many=True)
            return Response(data=serialized_posts.data)
        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='put', operation_description="Create a post with a given id", request_body=PostSerializer, responses={200: PostSerializer})
@swagger_auto_schema(method='get', operation_description="Get a post by id", responses={200: PostSerializer})
@swagger_auto_schema(method='delete', operation_description="Delete a post")
@swagger_auto_schema(method='post', operation_description="Update a post", request_body=PostSerializer, responses={200: PostSerializer})
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
            updated_post = PostSerializer(
                instance=post, data=post_data, partial=True)

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


@swagger_auto_schema(method='post', operation_description="Comment on a post", request_body=CommentSerializer, responses={200: CommentSerializer})
@swagger_auto_schema(method='get', operation_description="Get a comment", responses={200: CommentSerializer(many=True)})
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
            comments = Comment.objects.filter(post_id=post_id)[
                offset:offset+size]
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


@swagger_auto_schema(method='post', operation_description="Send an object to inbox, see https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/project.org#inbox")
@swagger_auto_schema(method='get', operation_description="Get a list of objects from inbox")
@swagger_auto_schema(method='delete', operation_description="Clear inbox")
@api_view(['POST', 'GET', 'DELETE'])
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

                inbox_item = Inbox(
                    content_object=serialized_like.instance, author_id=id)
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

                inbox_item = Inbox(
                    content_object=serialized_like.instance, author_id=id)
                inbox_item.save()

                comment_data = serialized_like.data

                return Response(data=comment_data)

            else:
                return Response("Wtf you tryna do", status=status.HTTP_400_BAD_REQUEST)

        elif type == "post":
            post_data = data
            post_data["author_id"] = id
            post = PostSerializer(data=post_data)

            if not post.is_valid():
                return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

            post.save()

            inbox_item = Inbox(content_object=post.instance, author_id=id)
            inbox_item.save()

            return Response(data=post.data)

        elif type == "comment":
            # TODO: find a better way to supply post id
            comment_data = request.data
            comment_data["post_id"] = request.data["post_id"]
            comment_data["author_id"] = request.data["author"]["id"]
            comment = CommentSerializer(data=comment_data)

            if not comment.is_valid():
                return Response(data=comment.errors, status=status.HTTP_400_BAD_REQUEST)

            comment.save()

            inbox_item = Inbox(content_object=comment.instance, author_id=id)
            inbox_item.save()

            return Response(data=comment.data)

        elif type == "Follow":
            return Response("not implemented")

    elif request.method == 'GET':
        inbox_items = Inbox.objects.filter(author_id=id).order_by('-created_at')
        serialized_inbox_items = InboxSerializer(inbox_items, many=True)
        data = {
            "type": "inbox",
            "author": f"{HOST}/authors/{id}",
            "items": serialized_inbox_items.data
        }
        return Response(data)

    elif request.method == 'DELETE':
        Inbox.objects.filter(author_id=id).delete()
        return Response(f"Cleared inbox for author with id: {id}")


@swagger_auto_schema(method='get', operation_description="get likes from a post", responses={200: PostLikeSerializer(many=True)})
@api_view(['GET'])
def post_likes(request, author_id, post_id):
    post_likes = PostLike.objects.filter(post_id=post_id)
    serialized_post_like = PostLikeSerializer(post_likes, many=True)
    return Response(data=serialized_post_like.data)


@swagger_auto_schema(method='get', operation_description="get likes from a comment", responses={200: CommentLikeSerializer(many=True)})
@api_view(['GET'])
def comment_likes(request, author_id, post_id, comment_id):
    comment_likes = CommentLike.objects.filter(comment_id=comment_id)
    serialized_comment_like = CommentLikeSerializer(comment_likes, many=True)
    return Response(data=serialized_comment_like.data)


@swagger_auto_schema(method='get', operation_description="get objects an author has liked")
@api_view(['GET'])
def liked(request, id):
    liked_comments = CommentLike.objects.filter(author_id=id)
    liked_posts = PostLike.objects.filter(author_id=id)

    serialized_liked_comments = CommentLikeSerializer(
        liked_comments, many=True)
    serialized_liked_posts = PostLikeSerializer(liked_posts, many=True)

    data = {
        "type": "liked",
        # TODO: find better way to combine
        "items": serialized_liked_posts.data + serialized_liked_comments.data
    }

    return Response(data)


@swagger_auto_schema(method='get', operation_description="Get a list of followers of an author", responses={200: AuthorSerializer(many=True)})
@ api_view(['GET'])
def followers(request, author_id):
    if request.method == 'GET':
        try:
            followers = Follower.objects.filter(author=author_id)
            serialized_followers = FollowerSerializer(followers, many=True)
            authors = Author.objects.filter(
                id__in=[x.get('follower') for x in serialized_followers.data])
            serialized_authors = AuthorSerializer(authors, many=True)

            return Response(data={
                "type": "followers",
                "items": serialized_authors.data
            })

        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='get', operation_description="See if foreign_author_id follows author_id")
@swagger_auto_schema(method='delete', operation_description="foreign_author_id unfollows author_id")
@swagger_auto_schema(method='put', operation_description="adds foreign_author_id as a follower of author_id")
@ api_view(['GET', 'DELETE', 'PUT'])
def author_followers(request, author_id, foreign_author_id):

    if request.method == 'GET':
        try:
            following = Follower.objects.filter(
                author=author_id, follower=foreign_author_id).first()

        # TODO: IDK IF ACTUAL RESPONSE - JUST SENDING 404
            if (following is None):
                return Response(data=f"Author with id: {foreign_author_id} is not following author: {author_id}", status=status.HTTP_404_NOT_FOUND)

        # TODO: IDK IF ACTUAL RESPONSE - JUST SENDING 200
            return Response(status=status.HTTP_200_OK)

        except:
            return Response(data="Error", status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        Follower.objects.filter(
            author=author_id, follower=foreign_author_id).delete()
        return Response(f"Cleared following of author: {foreign_author_id} for author: {author_id}", status=status.HTTP_200_OK)

    # TODO This method needs to be authenticated
    if request.method == 'PUT':
        follow_request = FollowerSerializer(
            data={"author": author_id, "follower": foreign_author_id})

        if not follow_request.is_valid():
            return Response(data=follow_request.errors, status=status.HTTP_400_BAD_REQUEST)

        follow_request.save()
        return Response(follow_request.data, status=status.HTTP_200_OK)
