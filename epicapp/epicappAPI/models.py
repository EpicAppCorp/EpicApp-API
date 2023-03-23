import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser


class Author(AbstractUser):
    type = "author"
    id = models.CharField(primary_key=True, max_length=255,
                          default=uuid.uuid4, editable=False)
    host = models.URLField(blank=False, editable=False)
    displayName = models.CharField(unique=True, max_length=36)
    url = models.URLField(blank=False, editable=False)
    password = models.CharField(max_length=255)
    github = models.URLField(unique=True)
    profileImage = models.TextField()

    # remove unused fields inherited from AbstractUser
    email = None
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'displayName'
    REQUIRED_FIELDS = []


class Post(models.Model):
    class ContentType(models.TextChoices):
        textMarkdown = 'text/markdown'
        textPlain = 'text/plain'
        # various image types
        appImg = 'application/base64'
        pngImg = 'image/png;base64'
        jpegImg = 'image/jpeg;base64'

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC'
        FRIENDS = 'FRIENDS'
        # TODO: PRIVATE

    type = "post"
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, max_length=255, unique=True)
    title = models.CharField(max_length=50)
    source = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True)
    content = models.TextField()
    contentType = models.CharField(max_length=18, choices=ContentType.choices)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(
        max_length=7, choices=Visibility.choices, default=Visibility.PUBLIC)
    categories = ArrayField(
        models.CharField(max_length=24),
        default=list
    )
    unlisted = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Comment(models.Model):
    type = "comment"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(max_length=500)
    contentType = "text/markdown"  # not sure if this can be anything else
    published = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Like(models.Model):
    type = "Like"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.URLField(blank=False, editable=False, null=False)
    object = models.URLField(blank=False, editable=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at', )


class Inbox(models.Model):
    class ObjectType(models.TextChoices):
        like = 'like'
        comment = 'comment'
        post = 'post'
        follower = 'follow'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=7, choices=ObjectType.choices)

    class Meta:
        ordering = ('created_at', )


class Follower(models.Model):
    id = models.CharField(primary_key=True, max_length=255,
                          default=uuid.uuid4, editable=False)
    author = models.CharField(max_length=255,
                              default=uuid.uuid4, editable=False)
    follower = models.TextField()

    class Meta:
        unique_together = (('author', 'follower'))


class Server(models.Model):
    url = models.TextField()
    token = models.TextField()
    issuer = models.TextField()


class InboxComment(models.Model):
    type = "comment"
    id = models.URLField(blank=False, unique=True, primary_key=True)
    comment = models.TextField(max_length=500)
    contentType = "text/markdown"  # not sure if this can be anything else
    published = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.URLField(blank=False, editable=False)
