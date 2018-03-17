from app.model.api import serializers
from .. import models


class FieldSerializer(serializers.FieldSerializer):
    class Meta(serializers.FieldSerializer.Meta):
        model = models.Field


class ClassifySerializer(serializers.ClassifySerializer):
    model_vehicle_classify = FieldSerializer(many=True, read_only=True)

    class Meta(serializers.ClassifySerializer.Meta):
        model = models.Classify
        fields = ('id', 'name', 'model_vehicle_classify', 'allow_foreign_compare')


class ModelSerializer(serializers.ModelSerializer):
    classify = ClassifySerializer(read_only=True)

    class Meta(serializers.ModelSerializer.Meta):
        model = models.Model
