from django.contrib.auth.models import User
from rest_framework import serializers

from shortener.models import ShortenedUrls, Users


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "url_count", "organization", "last_login", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "groups", "user_permissions"]


class UrlListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ShortenedUrls
        fields = ["id", "nick_name", "prefix", "shortened_url", "creator", "click", "create_via", "expired_at"]