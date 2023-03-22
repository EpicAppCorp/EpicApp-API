import jwt
import datetime
import base64
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils.swagger import SwaggerShape
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Author, Post, Comment, PostLike, CommentLike, Inbox, Follower, FollowRequest
from .config import HOST
from .utils.auth import authenticated
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer, InboxSerializer, FollowerSerializer, FollowRequestSerializer


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "host": openapi.Schema(type=openapi.TYPE_STRING),
                "displayName": openapi.Schema(type=openapi.TYPE_STRING),
                "github": openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def post(self, request, format=None):
        author = AuthorSerializer(data=request.data)

        if not author.is_valid():
            return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

        author.save()

        return Response(status=status.HTTP_201_CREATED)


class AuthenticateView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "displayName": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.author_details
                }
            )
        }
    )
    def post(self, request, format=None):
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),
                'iat': datetime.datetime.utcnow()
            }, "SECRET_NOT_USING_ENV_CAUSE_WHO_CARES", algorithm='HS256')

        serialized_author = AuthorSerializer(author).data

        # gets followers on login
        followers = Follower.objects.filter(
            author=serialized_author['id']).count()
        following = Follower.objects.filter(
            follower=f"{HOST}/api/authors/{serialized_author['id']}").count()

        # return an http only cookie, but if needed to make it easier, we can not do http only cookies so JS can use it.
        response = Response(data={**serialized_author, "followers": followers, "following": following},
                            status=status.HTTP_200_OK)
        response.set_cookie(key='access', value=token,
                            secure=True, httponly=True, samesite='Lax')

        # this one is for dev
        # response.set_cookie(key='access', value=token,
        #                     secure=False, samesite='Strict')
        return response


class LogoutView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def post(self, request, format=None):
        response = Response(data="Logout successful!",
                            status=status.HTTP_200_OK)
        response.delete_cookie('access')
        return response


class AuthorDetails(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.author_details
                }
            )
        }
    )
    @authenticated
    def get(self, request, format=None):
        followers = Follower.objects.filter(author=request._auth['id']).count()
        following = Follower.objects.filter(
            follower=f"{HOST}/api/authors/{request._auth['id']}").count()
        author = Author.objects.filter(id=request._auth['id']).first()
        return Response(data={**AuthorSerializer(author).data, "followers": followers, "following": following}, status=status.HTTP_200_OK)


class AuthorView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.author_details
                }
            )
        }
    )
    def get(self, request, id, format=None):
        author = Author.objects.filter(id=id).first()
        return Response(data=AuthorSerializer(author).data, status=status.HTTP_200_OK)


class AuthorsView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.author_list
                }
            )
        }
    )
    def get(self, request, format=None):
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))

        offset = (page - 1) * size
        authors = Author.objects.all()[
            offset:offset+size]
        serialized_authors = AuthorSerializer(authors, many=True)
        return Response(data={"type": "authors", "items": serialized_authors.data})


class PostsView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.post_list
                }
            )
        }
    )
    def get(self, request, author_id):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 5))

            offset = (page - 1) * size
            posts = Post.objects.filter(author_id=author_id)[
                offset:offset+size]
            serialized_posts = PostSerializer(posts, many=True)
            return Response(data=serialized_posts.data)
        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=SwaggerShape.post_request_body
        ),
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def post(self, request, author_id):
        post_data = request.data
        post_data["author_id"] = author_id
        post = PostSerializer(data=post_data)

        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        for follower_url in Follower.objects.filter(author=author_id).values_list("follower", flat=True):
            # TODO: PROPER BASIC AUTH FROM SERVER
            # fire and forget, if it doesn't make it to the follower oh well ¯\_(ツ)_/¯
            requests.post(f"{follower_url}/inbox", json=post.data,
                          headers={"Authorization": "Basic test"})

        return Response(data=post.data)


class PostView(APIView):

    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.post_detail
                }
            )
        }
    )
    def get(self, request, author_id, post_id):
        try:
            # TODO: WHY AUTHOR NOT BEING USED?
            author = Author.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)
            if post.visibility == Post.Visibility.FRIENDS:
                # ! note: this might change depending if we store foreign authors from friend requests
                followers_of_author = Follower.objects.filter(
                    author=post.author.id, follower="864decb1-ed95-4c85-b189-2e5216844853")
                # print(followers_of_author)
                if len(followers_of_author) == 0:
                    return Response(data="You don't have permission to view this post", status=status.HTTP_401_UNAUTHORIZED)
            serialized_post = PostSerializer(post)

            return Response(data=serialized_post.data)
        except Post.DoesNotExist as e:
            return Response(data="Post does not exist", status=status.HTTP_404_NOT_FOUND)
        except Author.DoesNotExist as e:
            return Response(data="Author does not exist", status=status.HTTP_404_NOT_FOUND)
        except Follower.DoesNotExist as e:
            return Response(data="bruh", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=SwaggerShape.post_request_body
        ),
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def post(self, request, author_id, post_id, format=None):
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

    def delete(self, request, author_id, post_id, format=None):
        affected_rows = Post.objects.filter(id=post_id).delete()
        if affected_rows[0] == 0:
            return Response(data=f"could not delete post with id \'{post_id}\'", status=status.HTTP_404_NOT_FOUND)
        return Response(data=affected_rows[0])

    def put(self, request, author_id, post_id, format=None):
        post_data = request.data
        post_data["id"] = post_id
        post_data["author_id"] = author_id
        post = PostSerializer(data=post_data)

        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        for follower_url in Follower.objects.filter(author=author_id).values_list("follower", flat=True):
            # TODO: PROPER BASIC AUTH FROM SERVER
            # fire and forget, if it doesn't make it to the follower oh well ¯\_(ツ)_/¯
            requests.post(f"{follower_url}/inbox", json=post.data,
                          headers={"Authorization": "Basic test"})

        return Response(data=post.data)


class PostImageView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json": SwaggerShape.post_detail_img
                }
            )
        }
    )
    def get(self, request, author_id, post_id):

        post = Post.objects.filter(id=post_id, author=author_id).first()

        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not post.contentType in [Post.ContentType.jpegImg, Post.ContentType.pngImg]:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(data=base64.b64decode(post.content),
                        content_type=post.contentType.split(";")[0])


class CommentsView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.comment_list
                }
            )
        }
    )
    def get(self, request, author_id, post_id):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 5))

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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=SwaggerShape.comment_request_body
        ),
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def post(self, request, author_id, post_id):
        comment_data = request.data
        comment_data["post_id"] = post_id
        comment_data["author_id"] = author_id
        comment = CommentSerializer(data=comment_data)

        if not comment.is_valid():
            return Response(data=comment.errors, status=status.HTTP_400_BAD_REQUEST)

        comment.save()

        return Response(data=comment.data)


class InboxView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.inbox_list
                }
            )
        }
    )
    @authenticated
    def get(self, request, id):
        inbox_items = Inbox.objects.filter(
            author_id=id).order_by('-created_at')
        data = []
        for inbox_item in inbox_items:
            if inbox_item.object_type == 'post':
                res = requests.get(inbox_item.object_id)
                data.append(res.json())

            elif inbox_item.object_type == 'follow':
                try:
                    follow_request = FollowRequest.objects.get(
                        id=inbox_item.object_id)
                    serialized_author = AuthorSerializer(follow_request.object)

                    res = requests.get(follow_request.actor)
                    actor = res.json()
                    data.append({
                        "type": inbox_item.object_type,
                        "summary": f"{actor['displayName']} wants to follow {serialized_author.data['displayName']}",
                        "actor": actor,
                        "object": serialized_author.data
                    })

                except FollowRequest.DoesNotExist:
                    return Response(data="something went wrong", status=status.HTTP_400_BAD_REQUEST)

        data = {
            "type": "inbox",
            "author": f"{HOST}/authors/{id}",
            "items": data
        }
        return Response(data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=SwaggerShape.follow_request_body
        ),
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def post(self, request, id):
        data = request.data
        type = data["type"]

        if type == "like":
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
            object_id = data["id"]
            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id": object_id,
                "object_type": type
            })

            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(data={}, status=status.HTTP_200_OK)

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

            return Response(data=post.data)

        elif type == "follow":
            new_follower = data['actor']['id']
            author_id = data['object']['id'].split('/')[-1]
            author = None

            try:
                author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)

            follow_request = FollowRequestSerializer(data={
                "actor": new_follower,
                "object_id": author_id
            })

            if not follow_request.is_valid():
                return Response(data=follow_request.errors, status=status.HTTP_400_BAD_REQUEST)

            follow_request.save()

            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id": follow_request.data['id'],
                "object_type": type
            })

            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(data={}, status=status.HTTP_200_OK)

    @authenticated
    def delete(self, request, id):
        Inbox.objects.filter(author_id=id).delete()
        return Response(f"Cleared inbox for author with id: {id}")


class LikesView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.likes_list
                }
            )
        }
    )
    def get(self, request, author_id, post_id):
        post_likes = PostLike.objects.filter(post_id=post_id)
        serialized_post_like = PostLikeSerializer(post_likes, many=True)
        return Response(data=serialized_post_like.data)


class CommentLikesView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.likes_list
                }
            )
        }
    )
    def get(self, request, author_id, post_id, comment_id):
        comment_likes = CommentLike.objects.filter(comment_id=comment_id)
        serialized_comment_like = CommentLikeSerializer(
            comment_likes, many=True)
        return Response(data=serialized_comment_like.data)


class LikedView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.liked_list
                }
            )
        }
    )
    def get(self, request, id):
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


class FollowersView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.follower_list
                }
            )
        }
    )
    def get(self, request, author_id):
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


class FollowerView(APIView):
    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
                examples={
                    "application/json":
                    SwaggerShape.author_details
                }
            )
        }
    )
    def get(self, request, author_id, foreign_author_id):
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

    @authenticated
    def delete(self, request, author_id, foreign_author_id):
        Follower.objects.filter(
            author=author_id, follower=foreign_author_id).delete()
        return Response(f"Cleared following of author: {foreign_author_id} for author: {author_id}", status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def put(self, request, author_id, foreign_author_id):
        follow_request = FollowerSerializer(
            data={"author": author_id, "follower": foreign_author_id})

        if not follow_request.is_valid():
            return Response(data=follow_request.errors, status=status.HTTP_400_BAD_REQUEST)

        follow_request.save()
        return Response(follow_request.data, status=status.HTTP_200_OK)
