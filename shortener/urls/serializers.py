from django.contrib.auth.models import User
from rest_framework import serializers

from shortener.models import ShortenedUrls, Users
from shortener.utils import url_count_changer


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
        fields = "__all__"


class UrlCreateSerializer(serializers.Serializer):
    nick_name = serializers.CharField(max_length=100)
    target_url = serializers.CharField(max_length=2000)
    category = serializers.IntegerField(required=False)

    def create(self, request, data, commit=True):
        instance = ShortenedUrls()
        instance.creator_id = request.user.id
        instance.category = data.get("category", None)
        instance.target_url = data.get("target_url").strip()
        instance.nick_name = data.get("nick_name")
        if commit:
            try:
                instance.save()
            except Exception as e:
                print(e)
            else:
                url_count_changer(request, True)
        return instance

class UrlCreateSerializer(serializers.Serializer):
    nick_name = serializers.CharField(max_length=100)
    target_url = serializers.CharField(max_length=2000)
    category = serializers.IntegerField(required=False)

    def create(self, request, data, commit=True):
        instance = ShortenedUrls()
        instance.creator_id = request.user.id
        instance.category = data.get("category", None)
        instance.target_url = data.get("target_url").strip()
        instance.nick_name = data.get("nick_name")
        if commit:
            try:
                instance.save()
            except Exception as e:
                print(e)
            else:
                url_count_changer(request, True)
        return instance