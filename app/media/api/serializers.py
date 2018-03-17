from rest_framework import serializers
from app.media.models import Image, Gallery, GalleryRelationship
from django.contrib.auth.models import User
from versatileimagefield.serializers import VersatileImageFieldSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ImageSerializer(serializers.ModelSerializer):
    path = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('medium_square_crop', 'crop__400x400'),
        ]
    )

    class Meta:
        model = Image
        fields = ['id', 'title', 'description', 'user', 'path', 'pub_date']
        read_only_fields = ('id', 'user', 'pub_date')


class GalleryUpdate(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    photos = serializers.SerializerMethodField()
    featured = ImageSerializer(read_only=True)

    class Meta:
        model = Gallery
        fields = ['id', 'title', 'description', 'featured', 'slug', 'photos', 'user', 'pub_date']
        read_only_fields = ('id', 'user', 'featured', 'slug', 'photos', 'pub_date')
        depth = 1

    def get_photos(self, obj):
        relations = GalleryRelationship.objects.filter(gallery=obj.id)
        images = []
        for relation in relations:
            images.append(relation.image)
        results = ImageSerializer(images, many=True).data
        return results
