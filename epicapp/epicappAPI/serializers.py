from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github', 'profile_image', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # hash password
        validated_data['password'] = make_password(validated_data['password'])
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):       
        instance.displayName = validated_data.get('displayName', instance.displayName)
        # instance.email = validated_data.get('email', instance.email)
        instance.host = validated_data.get('host', instance.host)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance
