import jwt
import datetime
import base64
import requests
import uuid
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils.swagger import SwaggerShape
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Author, Post, Comment, Inbox, Follower, Like, Server
from .config import HOST
from .utils.auth import authenticated
from .utils.path import get_url_id, get_path_id
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, InboxSerializer, FollowerSerializer, LikeSerializer


class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Register for a local account",
        operation_id="author_register",
        operation_summary="Register for a local account",
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
        if request.data['password'] != request.data['confirmpassword']:
            return Response(data={"passwords": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)

        author = AuthorSerializer(data=request.data)

        if not author.is_valid():
            return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

        author.save()

        return Response(status=status.HTTP_201_CREATED)


class AuthenticateView(APIView):
    @swagger_auto_schema(
        operation_description="Authenticates an author and sets a one year cookie for all other requests",
        operation_id="author_auth",
        operation_summary="Login a user and set a cookie",
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
        serialized_author = AuthorSerializer(author).data

        # create token with one year expiry
        token = jwt.encode(
            {
                'id': author.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),
                'iat': datetime.datetime.utcnow()
            }, "SECRET_NOT_USING_ENV_CAUSE_WHO_CARES", algorithm='HS256')

        # gets followers on login
        followers = Follower.objects.filter(
            author=serialized_author['id'], accepted=True).values_list('follower', flat=True)
        following = Follower.objects.filter(
            follower=serialized_author['id']).values_list('author', flat=True)

        # return an http only cookie, but if needed to make it easier, we can not do http only cookies so JS can use it.
        response = Response(data={**serialized_author, "followers": followers, "following": following},
                            status=status.HTTP_200_OK)

        response.set_cookie(key='access', value=token,
                            secure=True, samesite='None', path='/')

        # this one is for dev
        # response.set_cookie(key='access', value=token,
        #                     secure=False, samesite='Lax')
        return response


class LogoutView(APIView):
    @swagger_auto_schema(
        operation_description="Logouts a authenticated author by destroying the cookie",
        operation_id="author_logout",
        operation_summary="Logout a user and destroy cookie",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def post(self, request, format=None):
        response = Response(data="Logout successful!",
                            status=status.HTTP_200_OK)
        response.set_cookie('access', value='', max_age=0, path='/', secure=True,
                            samesite='None', expires='Thu, 01-Jan-1970 00:00:00 GMT')
        return response


class FriendsView(APIView):
    @authenticated
    def get(self, request, format=None):
        authors = Author.objects.exclude(id=request._auth['id']).all()
        serialized_authors = AuthorSerializer(authors, many=True)

        servers = Server.objects.all()
        friends = [*serialized_authors.data]
        for server in servers:
            req = requests.get(f"{server.url}/authors",
                               headers={"Authorization": server.token})
            friends = [*friends, *req.json()["items"]]

        return Response(data={"type": "friends", "items": friends})


class AuthorDetails(APIView):
    @swagger_auto_schema(
        operation_description="Gets the details of the currently authenticated author",
        operation_id="author_details_local",
        operation_summary="Get current users detail",
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

        author = Author.objects.filter(id=request._auth['id']).first()
        serialized_author = AuthorSerializer(author).data

        followers = Follower.objects.filter(
            author=serialized_author['id'], accepted=True).values_list('follower', flat=True)
        following = Follower.objects.filter(
            follower=serialized_author['id']).values_list('author', flat=True)
        return Response(data={**serialized_author, "followers": followers, "following": following}, status=status.HTTP_200_OK)


class AuthorView(APIView):
    @swagger_auto_schema(
        operation_description="Gets the details of an author with a specified id",
        operation_id="author_details",
        operation_summary="Gets the of a user by id",
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
        operation_description="Gets the details of all authors (paginated) (default page: 1, default size: 5)",
        operation_summary="Get authors (paginated)",
        operation_id="all_authors",
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
        operation_description="Get the list of posts of the author with a specified id (paginated) (default page: 1, default size: 5)",
        operation_summary="Get list of posts (paginated)",
        operation_id="all_author_posts",
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
            posts = Post.objects.filter(author_id=author_id).order_by('-published')[
                offset:offset+size]
            serialized_posts = PostSerializer(posts, many=True)
            return Response(data={"type": "posts", "items": serialized_posts.data})
        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Creates a post with a specified author id which is then sent to all followers of author.",
        operation_id="create_author_post",
        operation_summary="Createa a post",
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
        post_data["source"] = f"{HOST}/api/authors/{author_id}"
        post: Post = PostSerializer(data=post_data)

        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        # save to the original author
        inbox_to_og = InboxSerializer(data={
            "author_id": author_id,
            "object_id": post.data['id'],
            "object_type": "post"
        })
        if not inbox_to_og.is_valid():
            return Response(data=inbox_to_og.errors, status=status.HTTP_400_BAD_REQUEST)
        inbox_to_og.save()

        # if post.data['visibility'] == 'PUBLIC':
        #     return Response(data=post.data)

        for follower_url in Follower.objects.filter(author=get_url_id(author_id), accepted=True).values_list("follower", flat=True):
            # if url is from us, just get from models and not make another request to same server
            if (HOST in follower_url):
                inbox_item = InboxSerializer(data={
                    "author_id": follower_url.split('/')[-1],
                    "object_id": post.data['id'],
                    "object_type": "post"
                })
                if not inbox_item.is_valid():
                    return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)
                inbox_item.save()
            else:
                server = Server.objects.get(
                    url=follower_url.split('/authors/')[0])
                requests.post(f"{follower_url}/inbox/", json=post.data,
                              headers={"Authorization": server.token})

        return Response(data=post.data)


class PostView(APIView):
    @swagger_auto_schema(
        operation_description="Gets the details of a specified post. Will check the visibility of the post.",
        operation_summary="Gets details of a post",
        operation_id="get_author_post",
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
            post = Post.objects.get(id=post_id)
            if post.visibility == Post.Visibility.FRIENDS:
                followers_of_author = Follower.objects.filter(
                    author=post.author.id, follower=author_id)
                if len(followers_of_author) == 0:
                    return Response(data="You don't have permission to view this post", status=status.HTTP_401_UNAUTHORIZED)
            return Response(data=PostSerializer(post).data)
        except Post.DoesNotExist as e:
            return Response(data="Post does not exist", status=status.HTTP_404_NOT_FOUND)
        except Author.DoesNotExist as e:
            return Response(data="Author does not exist", status=status.HTTP_404_NOT_FOUND)
        except Follower.DoesNotExist as e:
            return Response(data="bruh", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Updates an existing post",
        operation_id="update_author_post",
        operation_summary="Update a post",
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

    @swagger_auto_schema(
        operation_description="Deletes an existing post",
        operation_id="delete_author_post",
        operation_summary="Delete a post",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def delete(self, request, author_id, post_id, format=None):
        affected_rows = Post.objects.filter(id=post_id).delete()
        if affected_rows[0] == 0:
            return Response(data=f"could not delete post with id \'{post_id}\'", status=status.HTTP_404_NOT_FOUND)
        return Response(data=affected_rows[0])

    @swagger_auto_schema(
        operation_description="Creates a new post with an existing id",
        operation_id="create_author_post_existing",
        operation_summary="Create a post with an existing ID",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    def put(self, request, author_id, post_id, format=None):
        post_data = request.data
        post_data["id"] = post_id
        post_data["author_id"] = author_id
        post_data["source"] = f"{HOST}/api/authors/{author_id}"
        post = PostSerializer(data=post_data)

        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        for follower_url in Follower.objects.filter(author=get_url_id(author_id), accepted=True).values_list("follower", flat=True):
            # TODO: PROPER BASIC AUTH FROM SERVER

            # if url is from us, just get from models and not make another request to same server
            if (HOST in follower_url):
                inbox_item = InboxSerializer(data={
                    "author_id": follower_url.split('/')[-1],
                    "object_id": post.data['id'],
                    "object_type": "post"
                })
                if not inbox_item.is_valid():
                    return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)
                inbox_item.save()
            else:
                server = Server.objects.get(
                    url=follower_url.split('/authors/')[0])
                requests.post(f"{follower_url}/inbox/", json=post.data,
                              headers={"Authorization": server.token})

        return Response(data=post.data)


class RepostView(APIView):
    def put(self, request, author_id):
        post_data = request.data

        del post_data['id']
        post_data["author_id"] = post_data['author']['id'].split('/')[-1]
        # latest source is us since we reposted it
        post_data['source'] = f"{HOST}/api/authors/{author_id}"
        post: Post = PostSerializer(data=post_data)

        if not post.is_valid():
            return Response(data=post.errors, status=status.HTTP_400_BAD_REQUEST)

        post.save()

        for follower_url in Follower.objects.filter(author=author_id).values_list("follower", flat=True):
            # TODO: PROPER BASIC AUTH FROM SERVER

            # if url is from us, just get from models and not make another request to same server
            if (HOST in follower_url):
                inbox_item = InboxSerializer(data={
                    "author_id": follower_url.split('/')[-1],
                    "object_id": post.data['id'],
                    "object_type": "post"
                })
                if not inbox_item.is_valid():
                    return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)
                inbox_item.save()
            else:
                server = Server.objects.get(
                    url=follower_url.split('/authors/')[0])
                requests.post(f"{follower_url}/inbox/", json=post_data,
                              headers={"Authorization": server.token})
        return Response()


class PostImageView(APIView):
    @swagger_auto_schema(
        operation_description="Returns the image of an existing post. If no image on post, returns 404.",
        operation_id="get_author_post_image",
        operation_summary="Get image of an existing image post",
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


class CommentView(APIView):
    def get(self, request, author_id, post_id, comment_id):
        print(f"{HOST}/api/authors/{author_id}/posts/{post_id}/comments/{comment_id}")
        try:
            comment = Comment.objects.filter(
                post_id=post_id, id=f"{HOST}/api/authors/{author_id}/posts/{post_id}/comments/{comment_id}").first()
            serialized_comment = CommentSerializer(comment).data

            return Response(data=serialized_comment)

        except Author.DoesNotExist:
            return Response(data=f"Author with id: {author_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response(data=f"Post with id: {post_id} does not exist", status=status.HTTP_404_NOT_FOUND)


class CommentsView(APIView):
    @swagger_auto_schema(
        operation_description="Gets the comments of a specified post (paginated) (default page: 1, default size: 5)",
        operation_summary="Gets the comments of a specified post (paginated)",
        operation_id="get_author_post_comments",
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
        operation_description="Adds a comment to a post",
        operation_summary="Add a comment to a post",
        operation_id="create_comment",
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
        comment_data["author"] = comment_data["author"]
        comment_data["id"] = f"{comment_data['post']}/comments/{uuid.uuid4()}"

        comment = CommentSerializer(data=comment_data)

        if not comment.is_valid():
            return Response(data=comment.errors, status=status.HTTP_400_BAD_REQUEST)

        comment.save()

        inbox_item = InboxSerializer(data={
            "author_id": author_id,
            "object_id": comment.data['id'],
            "object_type": "comment"
        })
        if not inbox_item.is_valid():
            return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)
        inbox_item.save()

        return Response(data=comment.data)


class InboxView(APIView):
    @swagger_auto_schema(
        operation_description="Gets the inbox of a specified author.",
        operation_summary="Get inbox of an author",
        operation_id="get_inbox",
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
    def get(self, request, id):
        # this part is just for unauthenticated users just to see local posts from our server
        if (id == "undefined"):
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 5))

            offset = (page - 1) * size
            posts = Post.objects.filter(visibility="PUBLIC")[
                offset:offset+size]
            serialized_posts = PostSerializer(posts, many=True)
            return Response(data={
                "type": "inbox",
                "author": f"{HOST}/authors/{id}",
                "items": serialized_posts.data
            })

        inbox_items = Inbox.objects.filter(
            author_id=id).order_by('-created_at')

        data = []
        for inbox_item in inbox_items:
            if inbox_item.object_type == 'post':
                post = ""

                # if url is from us, just get from models and not make another request to same server
                if (HOST in inbox_item.object_id):
                    post = PostSerializer(Post.objects.filter(
                        id=inbox_item.object_id.split('/')[-1]).first()).data
                else:
                    post = requests.get(inbox_item.object_id).json()

                data.append(post)

            elif inbox_item.object_type == 'like':

                like = Like.objects.get(id=inbox_item.object_id)
                formatted_like = LikeSerializer(like).data

                # format stuff
                del formatted_like['id']  # not needed in final representation
                like_type = "comment" if formatted_like['object'].split(
                    '/')[-2] == 'comments' else 'post'
                formatted_like['summary'] = f"{formatted_like['author']['displayName']} likes your {like_type}"

                data.append(formatted_like)

            elif inbox_item.object_type == 'follow':
                actor = ''

                # if url is from us, just get from models and not make another request to same server
                if (HOST in inbox_item.object_id):
                    actor = AuthorSerializer(Author.objects.filter(
                        id=inbox_item.object_id.split('/')[-1]).first()).data
                else:
                    actor = requests.get(inbox_item.object_id).json()

                data.append({
                    "type": inbox_item.object_type,
                    "summary": f"{actor['displayName']} wants to follow you",
                    "actor": actor,
                })

            elif inbox_item.object_type == 'comment':
                inbox_comment = Comment.objects.get(
                    id=inbox_item.object_id)
                formatted_comment = CommentSerializer(inbox_comment).data

                data.append(formatted_comment)

        data = {
            "type": "inbox",
            "author": f"{HOST}/api/authors/{id}",
            "items": data
        }
        return Response(data)

    @swagger_auto_schema(
        operation_description="Creates an item in the inbox for the specified author",
        operation_id="create_inbox_item",
        operation_summary="Create an item in the inbox",
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

        if type.upper() == "LIKE":
            url_components = data['object'].split('/')
            object_id = url_components[-1]
            if url_components[-2] == "posts":
                try:
                    Post.objects.get(id=object_id)
                except Post.DoesNotExist:
                    return Response(data="Post does not exist", status=status.HTTP_400_BAD_REQUEST)
            elif url_components[-2] == "comments":
                try:
                    Comment.objects.get(id=data['object'])
                except Post.DoesNotExist:
                    return Response(data="Post does not exist", status=status.HTTP_400_BAD_REQUEST)
                except Comment.DoesNotExist:
                    return Response(data="Comment does not exist", status=status.HTTP_400_BAD_REQUEST)

            if (HOST not in request.data['author']):
                server = Server.objects.get(
                    url=request.data['author'].split('/authors/')[0])
                requests.post(f"{request.data['author']}/liked", json={
                    "object": request.data['object'],
                }, headers={"Authorization": server.token})

            serialized_like = LikeSerializer(
                data={**data, 'object': data['object']})
            serialized_like.skip_representations = True

            if not serialized_like.is_valid():
                return Response(data=serialized_like.errors, status=status.HTTP_400_BAD_REQUEST)

            serialized_like.save()
            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id": serialized_like.data['id'],
                "object_type": "like"
            })

            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(status=status.HTTP_200_OK)

        elif type.upper() == "POST":
            object_id = data["id"]
            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id": object_id,
                "object_type": "post"
            })

            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(status=status.HTTP_200_OK)

        elif type.upper() == "COMMENT":
            comment_data = data
            comment_url = comment_data['post'].split('/')
            post_id = comment_url[-1]

            if post_id == '/':  # check for trailing /
                comment_url.pop()
                post_id = comment_url[-1]

            comment_data["post_id"] = post_id
            comment_data["author"] = data['author']
            comment_data["id"] = comment_data['post'] + \
                f"/comments/{uuid.uuid4()}"
            comment = CommentSerializer(data=comment_data)

            if not comment.is_valid():
                return Response(data=comment.errors, status=status.HTTP_400_BAD_REQUEST)

            comment.save()

            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id": comment.data['id'],
                "object_type": "comment"
            })
            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(data=comment.data)

        elif type.upper() == "FOLLOW":

            inbox_item = InboxSerializer(data={
                "author_id": id,
                "object_id":  data['actor']['url'],
                "object_type": "follow"
            })

            if not inbox_item.is_valid():
                return Response(data=inbox_item.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox_item.save()

            return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Deletes the entire inbox of specified author",
        operation_id="delete_inbox",
        operation_summary="Clear inbox",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def delete(self, request, id):
        Inbox.objects.filter(author_id=id).delete()
        return Response(f"Cleared inbox for author with id: {id}")


class LikesView(APIView):
    @swagger_auto_schema(
        operation_description="Gets all the likes of a specified post",
        operation_id="get_post_likes",
        operation_summary="Get all likes for a specified post",
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
        object = f"{HOST}/api/authors/{author_id}/posts/{post_id}"
        post_likes = Like.objects.filter(object=object)
        serialized_post_like = LikeSerializer(post_likes, many=True)

        data = {
            "type": "liked",
            # TODO: find better way to combine
            "items": serialized_post_like.data
        }
        return Response(data=data)

    @authenticated
    def post(self, request, author_id, post_id):
        author = HOST + f"/authors/{author_id}"
        object = author + f"/posts/{post_id}"

        # we save for tracking
        serialized_post_like = LikeSerializer(data={
            "author": author,
            "object": object
        })

        if not serialized_post_like.is_valid():
            return Response(data=serialized_post_like.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class CommentLikesView(APIView):
    @swagger_auto_schema(
        operation_description="Gets all the like of a comment of a specified post",
        operation_summary="Get all likes for a specified comment",
        operation_id="get_comment_likes",
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
        object = f"{HOST}/api/authors/{author_id}/posts/{post_id}/comments/{comment_id}"
        post_likes = Like.objects.filter(object=object)
        serialized_post_like = LikeSerializer(post_likes, many=True)

        data = {
            "type": "liked",
            # TODO: find better way to combine
            "items": serialized_post_like.data
        }
        return Response(data=data)


class LikedView(APIView):
    @swagger_auto_schema(
        operation_description="Gets all the likes of a specified author",
        operation_summary="Gets all things that an author liked",
        operation_id="get_author_likes",
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
        liked_objects = Like.objects.filter(author=get_url_id(id))

        serialized_liked_objects = LikeSerializer(liked_objects, many=True)

        data = {
            "type": "liked",
            # TODO: find better way to combine
            "items": serialized_liked_objects.data
        }

        return Response(data)

    @authenticated
    def post(self, request, id):
        object = request.data['object']  # this is a URL!!
        author = HOST + f"/api/authors/{id}"

        # we save for tracking
        serialized_post_like = LikeSerializer(data={
            "author": author,
            "object": object
        })

        if not serialized_post_like.is_valid():
            return Response(data=serialized_post_like.errors, status=status.HTTP_400_BAD_REQUEST)

        serialized_post_like.save()

        return Response(status=status.HTTP_200_OK)


class FollowersView(APIView):
    @swagger_auto_schema(
        operation_description="Gets all the followers of a specified author",
        operation_summary="Gets the followers of an author",
        operation_id="get_author_followers",
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
            followers = Follower.objects.filter(
                author=get_url_id(author_id), accepted=True)
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
        operation_description="See if foreign_author_id follows author_id",
        operation_summary="See if a foreign author follows one of our local ones",
        operation_id="is_following",
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
                author=get_url_id(author_id), follower=foreign_author_id, accepted=True).first()

        # TODO: IDK IF ACTUAL RESPONSE - JUST SENDING 404
            if (following is None):
                return Response(data=f"Author with id: {foreign_author_id} is not following author: {author_id}", status=status.HTTP_404_NOT_FOUND)

        # TODO: IDK IF ACTUAL RESPONSE - JUST SENDING 200
            return Response(status=status.HTTP_200_OK)

        except:
            return Response(data="Error", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="foreign_author_id unfollows author_id",
        operation_id="unfollow",
        operation_summary="Foreign author unfollows author",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def delete(self, request, author_id, foreign_author_id):
        follower_request = Follower.objects.filter(author=get_url_id(
            author_id), follower=foreign_author_id).first()

        new_request = FollowerSerializer(follower_request).data
        new_request['accepted'] = False

        allow_follower = FollowerSerializer(
            instance=follower_request, data=new_request, partial=True)

        if not allow_follower.is_valid():
            return Response(data=allow_follower.errors, status=status.HTTP_400_BAD_REQUEST)

        allow_follower.save()
        return Response(data=allow_follower.data["follower"], status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="author_id accepts foreign_author_id request and now follows",
        operation_summary="One of our local authors accepts a foreign authors request",
        operation_id="follow",
        responses={
            "200": openapi.Response(
                description="OK",
            )
        }
    )
    @authenticated
    def put(self, request, author_id, foreign_author_id):
        follower_request = Follower.objects.filter(author=get_url_id(
            author_id), follower=foreign_author_id).first()

        new_request = FollowerSerializer(follower_request).data
        new_request['accepted'] = True

        allow_follower = FollowerSerializer(
            instance=follower_request, data=new_request, partial=True)

        if not allow_follower.is_valid():
            return Response(data=allow_follower.errors, status=status.HTTP_400_BAD_REQUEST)

        allow_follower.save()
        return Response(data=allow_follower.data["follower"], status=status.HTTP_200_OK)

    @authenticated
    def post(self, request, author_id, foreign_author_id):
        if (Follower.objects.filter(author=foreign_author_id, follower=get_url_id(author_id)).exists()):
            return Response(status=status.HTTP_204_NO_CONTENT)

        follow_request = FollowerSerializer(
            data={"author": foreign_author_id, "follower": get_url_id(author_id)})

        if not follow_request.is_valid():
            return Response(data=follow_request.errors, status=status.HTTP_400_BAD_REQUEST)
        if (HOST in foreign_author_id):
            inbox = InboxSerializer(data={
                "author_id":  get_path_id(foreign_author_id),
                "object_id":  get_url_id(author_id),
                "object_type": "follow"
            })

            if not inbox.is_valid():
                return Response(data=inbox.errors, status=status.HTTP_400_BAD_REQUEST)

            inbox.save()
        else:
            server = Server.objects.get(
                url=foreign_author_id.split('/authors/')[0])
            requests.post(f"{ request.data['object']['author']['url']}/inbox", json={
                "type": 'follow',
                "summary": f'{request.data["actor"]["displayName"]} wants to follow {request.data["object"]["displayName"]}'
            },
                headers={"Authorization": server.token})

        follow_request.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
