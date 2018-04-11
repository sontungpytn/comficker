from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from app.thing import models
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from app.media.models import Gallery
from itertools import chain


class ThingViewSet(viewsets.ModelViewSet):
    models = models.Thing
    queryset = models.objects.all()
    serializer_class = serializers.ThingSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = permissions.AllowAny,
    search_fields = ['name', ]

    def get_queryset(self, *args, **kwargs):
        queryset_list = self.models.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)).distinct()
        return queryset_list

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        classify = models.Classify.objects.filter(slug=self.request.POST['classify_slug']).first()
        photos = Gallery.objects.filter(pk=self.request.POST['photos_id']).first()
        user = User.objects.get(pk=1)
        try:
            if photos:
                serializer.save(slug=slugify(self.request.POST['name']), classify=classify, creator=user,photos=photos)
            else:
                serializer.save(slug=slugify(self.request.POST['name']), classify=classify,
                                creator=user)
        except IntegrityError:
            msg = {"msg": "This name " + self.request.POST['name'] + " is duplicate!"}
            return Response(msg, status=status.HTTP_403_FORBIDDEN)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class FieldViewSet(viewsets.ModelViewSet):
    models = models.Field
    queryset = models.objects.all()
    serializer_class = serializers.FieldSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = permissions.AllowAny,
    search_fields = ['name', ]
    pagination_class = None

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get("classify"):
            classify_slug = self.request.GET.get("classify")
            classify = models.Classify.objects.filter(slug=classify_slug).first()
            queryset_list = self.models.objects.filter(classify=classify)
            for data in classify.parents():
                queryset_list = list(chain(queryset_list, self.models.objects.filter(classify=data)))
        else:
            queryset_list = self.models.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)).distinct()
        return queryset_list


class ClassifyFieldViewSet(viewsets.ModelViewSet):
    models = models.Classify
    queryset = models.objects.all()
    serializer_class = serializers.ClassifySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = None
