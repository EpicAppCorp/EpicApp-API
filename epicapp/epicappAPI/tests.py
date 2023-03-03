import datetime

from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Author, Post, Comment, PostLike, CommentLike, Inbox, Follower, FollowRequest

class AuthTests(APITestCase):
    def test_register(self):
        url = reverse('register')
        data = {"displayName":"testname", "password": "test", "github": "https://github.com/shanerrr"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(Author.objects.get().displayName, 'testname')

    def test_login(self):
        url = reverse('register')
        data = {"displayName":"testname", "password": "test", "github": "https://github.com/shanerrr"}
        response = self.client.post(url, data, format='json')

        url = reverse('authenticate')
        data = {"displayName":"testname", "password": "test"}
        response = self.client.post(url, data, format='json')
        self.assertEqual("token" in response.cookies, True)

    def test_logout(self):
        url = reverse('logout')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuthorTests(APITestCase):
    def test_get_author(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        response = self.client.get(f'/api/author/{str(author.id)}', format='json')
        self.assertEqual(response.data['displayName'], 'testname')

    def test_get_authors(self):
        Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        Author.objects.create(displayName="testname1", password="test", github="https://github.com/shanerrr111")

        response = self.client.get('/api/authors', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class PostTests(APITestCase):
    def test_create_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")

        data = {
            "title": "this is a title",
            "source": "http://localhost:8000",
            "origin": "http://localhost:8000",
            "description": "this is a a super cool post",
            "content": "something jweioas jdflfa jsl;kjdfasklh fdoisau hdf",
            "contentType": "text/plain",
            "published": "uhhh",
            "visibility": "PUBLIC",
            "categories": ["something", "anothring thing"],
            "unlisted": False,
            "author": {
                "type": "author",
                "id": str(author.id),
                "host": "http://localhost:8000",
                "displayName": "testusername",
                "url": "http://localhost:8000",
                "github": "githubsthff",
                "profile_image": "more images stuff"
            }
        }
        response = self.client.post(f"/api/authors/{str(author.id)}/posts", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'this is a title')

    def test_get_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )

        response = self.client.get(f"/api/authors/{str(author.id)}/posts/{str(post.id)}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "bruh")


    def test_get_posts(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )

        response = self.client.get(f"/api/authors/{str(author.id)}/posts", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )

        response = self.client.delete(f"/api/authors/{str(author.id)}/posts/{str(post.id)}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Post.objects.all()), 0)

    def test_update_post(self):
        # response = self.client.post(f"/api/authors/{str(author.id)}/posts/{str(post.id)}", format='json')
        pass

    def test_create_post_with_id(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")

        data = {
            "title": "this is a title",
            "source": "http://localhost:8000",
            "origin": "http://localhost:8000",
            "description": "this is a a super cool post",
            "content": "something jweioas jdflfa jsl;kjdfasklh fdoisau hdf",
            "contentType": "text/plain",
            "published": "uhhh",
            "visibility": "PUBLIC",
            "categories": ["something", "anothring thing"],
            "unlisted": False,
            "author": {
                "type": "author",
                "id": str(author.id),
                "host": "http://localhost:8000",
                "displayName": "testusername",
                "url": "http://localhost:8000",
                "github": "githubsthff",
                "profile_image": "more images stuff"
            }
        }
        response = self.client.put(f"/api/authors/{str(author.id)}/posts/ac294663-07a6-4ab8-9122-bf435aa56a1d", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'this is a title')
        self.assertEqual(Post.objects.get().id, 'ac294663-07a6-4ab8-9122-bf435aa56a1d')


class CommentTests(APITestCase):
    def test_comment_on_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )

        comment_data = {
            "type":"comment",
            "author": {
                "type": "author",
                "id": str(author.id),
                "host": "http://localhost:8000",
                "displayName": "testusername",
                "url": "http://localhost:8000",
                "github": "githubsthff",
                "profile_image": "more images stuff"
            },
            "comment":"Sick Olde English",
            "contentType":"text/markdown",
            "published":"2015-03-09T13:07:04+00:00",
        }

        response = self.client.post(f"/api/authors/{str(author.id)}/posts/{str(post.id)}/comments", comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Sick Olde English')

    def test_get_comments_on_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )
        comment = Comment.objects.create(
            comment="comment text",
            published=datetime.datetime.now(),
            post_id=str(post.id),
            author_id=str(author.id)
        )
        response = self.client.get(f"/api/authors/{str(author.id)}/posts/{str(post.id)}/comments", format='json')
        self.assertEqual(len(response.data['comments']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LikeTests(APITestCase):
    def test_like_post(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )
        data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "Lara Croft Likes your post",         
            "type": "Like",
            "author": {
                "type": "author",
                "id": str(author.id),
                "host": "http://localhost:8000",
                "displayName": "testusername",
                "url": "http://localhost:8000",
                "github": "githubsthff",
                "profile_image": "more images stuff"
            },
            "object": f"http://127.0.0.1:5454/authors/{str(author.id)}/posts/{str(post.id)}"
        }
        response = self.client.post(f"/api/authors/{str(author.id)}/inbox", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_like_comment(self):
        author = Author.objects.create(displayName="testname", password="test", github="https://github.com/shanerrr")
        post = Post.objects.create(
            title="bruh",
            source="http://localhost:8000",
            origin="http://localhost:8000",
            description="sldfkjkldsjflks",
            contentType="text/plain",
            content="something stufnsdfjl",
            author_id=str(author.id)
        )
        comment = Comment.objects.create(
            comment="comment text",
            published=datetime.datetime.now(),
            post_id=str(post.id),
            author_id=str(author.id)
        )
        data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "Lara Croft Likes your post",         
            "type": "Like",
            "author": {
                "type": "author",
                "id": str(author.id),
                "host": "http://localhost:8000",
                "displayName": "testusername",
                "url": "http://localhost:8000",
                "github": "githubsthff",
                "profile_image": "more images stuff"
            },
            "object": f"http://127.0.0.1:5454/authors/{str(author.id)}/posts/{str(post.id)}/comments/{str(comment.id)}"
        }
        response = self.client.post(f"/api/authors/{str(author.id)}/inbox", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 


class FollowerTests(APITestCase):
    pass
