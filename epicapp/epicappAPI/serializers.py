import uuid
import requests

from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Author, Post, Comment, Inbox, Follower, Like
from .config import HOST


class AuthorSerializer(serializers.ModelSerializer, ):
    profileImage = serializers.CharField(required=False)

    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName',
                  'url', 'github', 'profileImage', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        id = uuid.uuid4()
        validated_data['id'] = id
        validated_data['url'] = f"{HOST}/api/authors/{id}"
        validated_data['host'] = f"{HOST}/"
        validated_data[
            'profileImage'] = f"https://api.dicebear.com/5.x/micah/svg?backgroundColor=fffd01&seed={id}"
        # hash password
        validated_data['password'] = make_password(validated_data['password'])
        return Author.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = f"{HOST}/api/authors/{instance.id}"
        return representation

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
        validated_data['origin'] = f"{HOST}/api/authors/{validated_data['author_id']}"
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = f"{HOST}/api/authors/{instance.author.id}/posts/{instance.id}"
        return representation


class CommentSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()
    author = serializers.URLField(required=True)
    post_id = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'type', 'comment', 'contentType',
                  'published', 'post_id', 'author']

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.published = validated_data.get(
            'published', instance.published)
        instance.contentType = validated_data.get(
            'contentType', instance.contentType)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # if url is from us, just get from models and not make another request to same server
        if (HOST in representation['author']):
            representation['author'] = AuthorSerializer(Author.objects.filter(
                id=representation['author'].split('/')[-1]).first()).data
        else:
            representation['author'] = requests.get(
                representation['author']).json()
        return representation


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

        # if url is from us, just get from models and not make another request to same server
        if (HOST in representation['author']):
            representation['author'] = AuthorSerializer(Author.objects.filter(
                id=representation['author'].split('/')[-1]).first()).data
        else:
            representation['author'] = requests.get(
                representation['author']).json()
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
