from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from app.model_food import models
from app.media import models as media
from . import serializers
from django.utils.text import slugify


class ClassifyViewSet(viewsets.ModelViewSet):

    models = models.Classify
    queryset = models.objects.all()
    serializer_class = serializers.ClassifySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = permissions.AllowAny,
    search_fields = ['name', ]
    pagination_class = None

    def get_queryset(self, *args, **kwargs):
        queryset_list = self.models.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                    ).distinct()
        return queryset_list


class ModelViewSet(viewsets.ModelViewSet):
    models = models.Model
    queryset = models.objects.all()
    serializer_class = serializers.ModelSerializer
    permission_classes = permissions.AllowAny,

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.request.POST['gallery'] is None:
            return Response({'Gallery': 'Please choose a gallery!'}, status=status.HTTP_400_BAD_REQUEST)
        gallery = media.Gallery.objects.filter(pk=self.request.POST['gallery']).first()
        serializer.save(slug=slugify(self.request.POST['name']),
                        user=request.user,
                        gallery=gallery)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if self.request.POST['gallery'] is None:
            return Response({'Gallery': 'Please choose a gallery!'}, status=status.HTTP_400_BAD_REQUEST)
        gallery = media.Gallery.objects.filter(pk=self.request.POST['gallery']).first()
        serializer.save(gallery=gallery)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)