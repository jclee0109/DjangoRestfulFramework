from django.http import Http404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from shortener.models import ShortenedUrls
from shortener.urls.serializers import UrlListSerializer, UrlCreateSerializer
from shortener.utils import url_count_changer, MsgOk


class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewd or edited
    """
    queryset = ShortenedUrls.objects.order_by("-created_at")
    serializer_class = UrlListSerializer
    permission_classes = [permissions.IsAuthenticated] #로그인 된 user만 이 api를 이용할 수 있음

    def create(self, request):
        #POST METHOD
        serializer = UrlCreateSerializer(data=request.data)
        if serializer.is_valid():
            rtn = serializer.create(request, serializer.data)
            return Response(UrlListSerializer(rtn).data, status=status.HTTP_201_CREATED)
        pass

    def retrieve(self, request, pk=None):
        #Detail GET
        queryset = self.get_queryset().filter(pk=pk).first()
        serializer = UrlListSerializer(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        #PUT METHOD
        pass

    def partial_update(self, request, pk=None):
        #PATCH METHOD
        pass

    @renderer_classes([JSONRenderer])
    def destroy(self, request, pk=None):
        #DELETE METHOD
        queryset = self.get_queryset().filter(pk=pk, creator_id=request.user.id)
        if not queryset.exists():
            raise Http404
        queryset.delete()
        url_count_changer(request, False)
        return MsgOk()

    def list(self, request):
        # GET ALL
        queryset = self.get_queryset().all()
        serializer = UrlListSerializer(queryset, many=True)
        return Response(serializer.data)



