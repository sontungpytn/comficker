import json
from django.db.models import Q
from django.utils.text import slugify
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics, permissions
from rest_framework import status, pagination
from rest_framework.response import Response
from app.media.models import Image, GalleryRelationship, Gallery
from app.utils import json_handle
from .permissions import IsOwnerOrReadOnly
from .serializers import ImageSerializer, GalleryUpdate


ERROR_FEATURED = "The featured image invalid!"
ERROR_PHOTOS = "Please add some valid photo to your gallery!"


class APIListImage(generics.ListAPIView):

    serializer_class = ImageSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']

    def get_queryset(self, *args, **kwargs):
        queryset_list = Image.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                    ).distinct()
        return queryset_list


class APIDetailImage(generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'id'
    permission_classes = permissions.AllowAny,


class APICreateImage(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = permissions.IsAuthenticated,

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        pub_date=timezone.now())


class APIUpdateImage(generics.RetrieveUpdateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'id'
    permission_classes = IsOwnerOrReadOnly,

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class APIDeleteImage(generics.DestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'id'
    permission_classes = IsOwnerOrReadOnly,


class APIListAlbum(generics.ListAPIView):

    serializer_class = GalleryUpdate
    permission_classes = permissions.AllowAny,
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']

    def get_queryset(self, *args, **kwargs):
        queryset_list = Gallery.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                    ).distinct()
        return queryset_list


class APICreateGallery(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = GalleryUpdate
    permission_classes = permissions.IsAuthenticated,

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slug = slugify(self.request.POST['title'])
        index = 0
        while not Gallery.objects.filter(slug=slug).first() is None:
            index = index + 1
            slug = slug + '-' +str(index)
        error_data = {'Featured': [], 'Photos': []}
        # Get Featured Image
        featured_image = ''
        try:
            if not json_handle.is_json(self.request.POST['featured']):
                error_data['Featured'].append(ERROR_FEATURED)
            else:
                featured = json.loads(self.request.POST['featured'])
        except MultiValueDictKeyError:
            error_data['Featured'].append(ERROR_FEATURED)
        # Get List images

        try:
            if not json_handle.is_json(self.request.POST['images']):
                error_data['Photos'].append(ERROR_PHOTOS)
            else:
                images = json.loads(self.request.POST['images'])
                if not images:
                    error_data['Photos'].append(ERROR_PHOTOS)
        except MultiValueDictKeyError:
            error_data['Photos'].append(ERROR_PHOTOS)

        # Check
        if error_data['Featured'] or error_data['Photos']:
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        if featured:
            img = Image.objects.filter(pk=featured['id']).get()
            featured_image = img
        else:
            img = Image.objects.filter(pk=images[0]['id']).get()
            featured_image = img

        # Save
        serializer.save(user=self.request.user,
                        pub_date=timezone.now(),
                        featured=featured_image,
                        slug=slug)

        gallery = Gallery.objects.filter(pk=serializer.data['id']).get()
        for image_raw in images:
            image = Image.objects.filter(pk=image_raw['id']).get()
            relationship = GalleryRelationship(image=image, gallery=gallery, pub_date=timezone.now())
            relationship.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class APIUpdateGallery(generics.RetrieveUpdateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GalleryUpdate
    lookup_field = 'id'
    permission_classes = permissions.IsAuthenticated, IsOwnerOrReadOnly,

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        gallery_obj = Gallery.objects.filter(pk=int(kwargs['id'])).get()
        gallery = GalleryUpdate(gallery_obj).data
        error_data = {'Photos': []}

        # Get List images
        try:
            if json_handle.is_json(self.request.POST['images']):
                images = json.loads(self.request.POST['images'])
                if images:
                    for relationship in GalleryRelationship.objects.filter(gallery=gallery_obj):
                        relationship.delete()
                    for image_raw in images:
                        image = Image.objects.filter(pk=image_raw['id']).get()
                        relationship = GalleryRelationship(image=image, gallery=gallery_obj, pub_date=timezone.now())
                        relationship.save()
                else:
                    images = gallery['photos']
            else:
                images = gallery['photos']
        except MultiValueDictKeyError:
            images = gallery['photos']

        # Check
        if error_data['Photos']:
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        # Get Featured Image
        featured_temp = Image.objects.filter(pk=images[0]['id']).get()
        try:
            if json_handle.is_json(self.request.POST['featured']):
                featured = json.loads(self.request.POST['featured'])
                if featured:
                    img = Image.objects.filter(pk=featured['id']).get()
                    featured_image = img
                else:
                    featured_image = featured_temp
            else:
                featured_image = featured_temp
        except MultiValueDictKeyError:
            featured_image = featured_temp

        serializer.save(featured=featured_image)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)