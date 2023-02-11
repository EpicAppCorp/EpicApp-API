import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

class Author(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(unique=True, max_length=36)
    email = models.EmailField(unique=True, max_length=64)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    github = models.CharField(unique=True, max_length=255)
    profile_image = models.TextField()

    # remove unused fields inherited from AbstractUser
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'displayName'


class Post(models.Model):
    class PostType(models.TextChoices):
        IMG_URL = 'IU' # img url: https://something.com/img.png
        IMG = 'IM' # base 64 image
        TEXT = 'TX'
        COMMON_MARK = 'CM'
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.TextField()
    type = models.CharField(max_length=2, choices=PostType.choices,)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(max_length=500)
    date = models.DateField(auto_now_add=True)
    comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

# todo:
# class Friend(models.Model):
#     id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
#     friendId = 
#     authorAccepted = models.BooleanField(default=False, null=False)
#     friendAccepted = models.BooleanField(default=False, null=False)

# Todo:
# class Inbox(models.Model):
#     pass
