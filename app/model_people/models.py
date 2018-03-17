from __future__ import unicode_literals
from django.db import models as django_models
from app.model import models as our_models

# Create your models here.


model_name = 'model_people'


class Classify(our_models.Classify):
    class Meta(our_models.Model.Meta):
        db_table = model_name + '_classify'


class Field(our_models.Field):
    classify = django_models.ForeignKey(Classify, on_delete=django_models.CASCADE,
                                        related_name=model_name + '_classify')

    class Meta(our_models.Model.Meta):
        db_table = model_name + '_field'


class Model(our_models.Model):
    classify = Classify

    class Meta(our_models.Model.Meta):
        db_table = model_name


class Vote(our_models.Vote):
    model = django_models.ForeignKey(Model, on_delete=django_models.CASCADE, default=None)

    class Meta(our_models.Vote.Meta):
        db_table = model_name + '_vote'


class Review(our_models.Review):
    first = django_models.ForeignKey(Model, on_delete=django_models.CASCADE, related_name=model_name + '_review_first',
                                     default=None)
    second = django_models.ForeignKey(Model, on_delete=django_models.CASCADE,
                                      related_name=model_name + '_review_second',
                                      default=None)

    class Meta(our_models.Review.Meta):
        db_table = model_name + '_review'
