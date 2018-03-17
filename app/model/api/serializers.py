from rest_framework import serializers
from app.model import models
from app.media import models as media


class GallerySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = media.Gallery
        fields = ['id', 'title']


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Field
        fields = ('id', 'name', 'data')


class ClassifySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Classify
        fields = ('id', 'name', 'model_vehicle_classify', 'allow_foreign_compare')


class ModelSerializer(serializers.HyperlinkedModelSerializer):
    gallery = GallerySerializer(read_only=True)
    classify = ClassifySerializer(read_only=True)

    class Meta:
        model = models.Model
        fields = ('id', 'name', 'slug', 'gallery', 'properties', 'pub_date')
        read_only_fields = ('id', 'slug', 'pub_date')
