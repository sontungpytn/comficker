from app.model.api import views
from . import serializers
from .. import models as model_temp


class ClassifyViewSet(views.ClassifyViewSet):
    models = model_temp.Classify
    serializer_class = serializers.ClassifySerializer


class ModelViewSet(views.ModelViewSet):
    models = model_temp.Model
    serializer_class = serializers.ModelSerializer
