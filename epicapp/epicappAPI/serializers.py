import uuid
import requests

from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Author, Post, Comment, Inbox, Follower, Server, InboxComment, Like
from .config import HOST


class AuthorSerializer(serializers.ModelSerializer):
    profileImage = serializers.CharField(required=False)

    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName',
                  'url', 'github', 'profileImage', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        id = uuid.uuid4()
        validated_data['id'] = f"{HOST}/api/authors/{id}"
        validated_data['url'] = f"{HOST}/api/authors/{id}"
        validated_data['host'] = f"{HOST}/"
        validated_data[
            'profileImage'] = f"https://api.dicebear.com/5.x/micah/svg?backgroundColor=fffd01&seed={id}"
        # hash password
        validated_data['password'] = make_password(validated_data['password'])
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.displayName = validated_data.get(
            'displayName', instance.displayName)
        instance.host = validated_data.get('host', instance.host)
        instance.github = validated_data.get('github', instance.github)
        instance.profileImage = validated_data.get(
            'profileImage', instance.profileImage)
        instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'source', 'origin', 'description', 'content', 'contentType',
                  'published', 'visibility', 'categories', 'unlisted', 'author', 'type', 'author_id']

    def create(self, validated_data):
        id = uuid.uuid4()
        validated_data['id'] = f"{HOST}/api/authors/{validated_data['author_id']}/posts/{id}"
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.source = validated_data.get('source', instance.source)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.content = validated_data.get('content', instance.content)
        instance.contentType = validated_data.get(
            'contentType', instance.contentType)
        instance.published = validated_data.get(
            'published', instance.published)
        instance.visibility = validated_data.get(
            'visibility', instance.visibility)
        instance.categories = validated_data.get(
            'categories', instance.categories)
        instance.unlisted = validated_data.get('unlisted', instance.unlisted)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only=True)
    post_id = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'type', 'comment', 'contentType',
                  'published', 'post_id', 'author', 'author_id']

    def create(self, validated_data):
        id = uuid.uuid4()
        validated_data['id'] = f"{HOST}/api/authors/{validated_data['author_id']}/posts/{validated_data['post_id']}/comments/{id}"
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.published = validated_data.get(
            'published', instance.published)
        instance.contentType = validated_data.get(
            'contentType', instance.contentType)
        instance.save()
        return instance


class InboxCommentSerializer(serializers.ModelSerializer):
    id = serializers.URLField(required=True)
    type = serializers.ReadOnlyField()
    author = serializers.URLField(required=True)
    post_id = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'type', 'comment', 'contentType',
                  'published', 'post_id', 'author']

    def create(self, validated_data):
        return InboxComment.objects.create(**validated_data)


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.URLField()
    object = serializers.URLField()

    class Meta:
        model = Like
        fields = ['id', 'type', 'author', 'object']

    def create(self, validated_data):
        return Like.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["@context"] = "https://www.w3.org/ns/activitystreams"
        res = requests.get(representation['author'])
        if not res.ok:
            raise Exception("error getting author")
        representation['author'] = res.json()
        return representation


class InboxSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(write_only=True)

    class Meta:
        model = Inbox
        fields = ['object_id', 'object_type', 'author_id']

    def create(self, validated_data):
        return Inbox.objects.create(**validated_data)


class FollowerSerializer(serializers.ModelSerializer):
    author = serializers.CharField()
    follower = serializers.CharField()

    class Meta:
        model = Follower
        fields = ['id', 'author', 'follower']

    def create(self, validated_data):
        return Follower.objects.create(**validated_data)


class ConnectedServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Server
        fields = ['url']

    def create(self, validated_data):
        return Server.objects.create(**validated_data)
