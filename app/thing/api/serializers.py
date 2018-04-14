from rest_framework import serializers
from app.thing import models
from app.media import models as media
from app.media.api.views import ImageSerializer


class GallerySerializer(serializers.HyperlinkedModelSerializer):
    featured = ImageSerializer(read_only=True)

    class Meta:
        model = media.Gallery
        fields = ['id', 'title', 'featured']


class SimpleFieldSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Field
        fields = ('id', 'name', 'slug')


class SimpleClassifySerializer(serializers.HyperlinkedModelSerializer):
    field = serializers.SerializerMethodField()

    class Meta:
        model = models.Classify
        fields = ('id', 'name', 'slug', 'description', 'field')

    def get_field(self, obj):
        return SimpleFieldSerializer(obj.field_child(), many=True).data


class ClassifySerializer(serializers.HyperlinkedModelSerializer):
    master_parent = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    field = serializers.SerializerMethodField()

    class Meta:
        model = models.Classify
        fields = ('id', 'name', 'slug', 'description', 'allow_foreign_compare', 'master_parent', 'parent', 'field')

    def get_master_parent(self, obj):
        return SimpleClassifySerializer(obj.master_parent()).data

    def get_parent(self, obj):
        return SimpleClassifySerializer(obj.parents(), many=True).data

    def get_field(self, obj):
        return SimpleFieldSerializer(obj.field_child(), many=True).data


class ThingSerializer(serializers.HyperlinkedModelSerializer):
    photos = GallerySerializer(read_only=True)
    classify = ClassifySerializer(read_only=True)

    class Meta:
        model = models.Thing
        fields = ('id', 'name', 'description', 'slug', 'data', 'photos', 'classify', 'created_date')
        read_only_fields = ('id', 'slug', 'created_date')


class FieldSerializer(serializers.HyperlinkedModelSerializer):
    classify = ClassifySerializer(read_only=True)

    class Meta:
        model = models.Field
        fields = ('id', 'name', 'slug', 'classify')
