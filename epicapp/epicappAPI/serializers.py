from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Author, Post, Comment, PostLike, CommentLike
from .config import HOST


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName',
                  'url', 'github', 'profile_image', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # hash password
        validated_data['password'] = make_password(validated_data['password'])
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.displayName = validated_data.get(
            'displayName', instance.displayName)
        instance.host = validated_data.get('host', instance.host)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get(
            'profile_image', instance.profile_image)
        instance.save()
        return instance

class PostSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only = True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'source', 'origin', 'description', 'content', 'contentType', 'published', 'visibility', 'categories', 'unlisted', 'author', 'type', 'author_id']

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.source = validated_data.get('source', instance.source)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.description = validated_data.get('description', instance.description)
        instance.content = validated_data.get('content', instance.content)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.published = validated_data.get('published', instance.published)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.categories = validated_data.get('categories', instance.categories)
        instance.unlisted = validated_data.get('unlisted', instance.unlisted)
        instance.save()
        return instance 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = f"{HOST}/api/authors/{instance.author.id}/posts/{instance.id}"
        return representation

class CommentSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only = True)
    post_id = serializers.CharField(write_only = True)

    class Meta:
        model = Comment
        fields = ['id', 'type', 'comment', 'contentType', 'published', 'post_id', 'author', 'author_id']

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.published = validated_data.get('published', instance.published)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.save()
        return instance 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = f"{HOST}/api/authors/{instance.author.id}/posts/{instance.post.id}/comments/{instance.id}"
        return representation

class PostLikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only = True)
    post_id = serializers.CharField(write_only = True)

    class Meta:
        model = PostLike
        fields = ['type', 'author', 'author_id', 'post_id']

    def create(self, validated_data):
        return PostLike.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["@context"] = "https://www.w3.org/ns/activitystreams"
        representation["summary"] = f"{instance.author.displayName} Likes your post"
        representation["object"] =  f"{HOST}/api/authors/{instance.author.id}/posts/{instance.post_id}"
        return representation

class CommentLikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.CharField(write_only = True)
    comment_id = serializers.CharField(write_only = True)

    class Meta:
        model = CommentLike
        fields = ['id', 'type', 'author', 'author_id', 'comment_id']

    def create(self, validated_data):
        return CommentLike.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["@context"] = "https://www.w3.org/ns/activitystreams"
        representation["summary"] = f"{instance.author.displayName} Likes your comment"
        return representation
