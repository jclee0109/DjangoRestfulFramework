from rest_framework import viewsets, permissions

from shortener.models import ShortenedUrls
from shortener.urls.serializers import UrlListSerializer


class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewd or edited
    """
    queryset = ShortenedUrls.objects.all().order_by("-created_at")
    serializer_class = UrlListSerializer
    permission_classes = [permissions.IsAuthenticated] #로그인 된 user만 이 api를 이용할 수 있음