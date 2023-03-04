import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Author(AbstractUser):
    type = models.CharField(max_length=255, default="author", editable=False)
    id = models.CharField(primary_key=True, max_length=255,
                          default=uuid.uuid4, editable=False)
    host = models.URLField(blank=False, editable=False)
    displayName = models.CharField(unique=True, max_length=36)
    url = models.URLField(blank=False, editable=False)
    password = models.CharField(max_length=255)
    github = models.URLField(unique=True)
    profile_image = models.TextField()

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


class PostLike(models.Model):
    type = "Like"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class CommentLike(models.Model):
    type = "Like"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Inbox(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at', )


class Follower(models.Model):
    id = models.CharField(primary_key=True, max_length=255,
                          default=uuid.uuid4, editable=False)
    author = models.CharField(max_length=255,
                              default=uuid.uuid4, editable=False)
    follower = models.CharField(max_length=255,
                                default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = (('author', 'follower'))


class FollowRequest(models.Model):
    type = "Follow"
    actor = models.ForeignKey(
        Author, on_delete=models.CASCADE,  related_name='follower')
    object = models.ForeignKey(
        Author, on_delete=models.CASCADE,  related_name='followee')
