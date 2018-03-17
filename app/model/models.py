from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models

from app.media import models as media


class Classify(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.CharField(max_length=60, unique=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True,
                               related_name='%(app_label)s_%(class)s_classifies_parent', default=0)
    allow_foreign_compare = models.IntegerField()
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Field(models.Model):
    name = models.CharField(max_length=60, unique=True)
    data = ArrayField(models.CharField(max_length=60, unique=True))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Model(models.Model):
    classify = Classify
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    gallery = models.ForeignKey(media.Gallery, null=True, on_delete=models.SET_NULL, blank=True,
                                related_name='%(app_label)s_%(class)s_gallery')
    properties = JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_creator')
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def classifies(self):
        data = []
        for property_temp in self.properties:
            if property_temp.get('active'):
                data.append(self.classify.objects.filter(name=property_temp['class']).first())
        return set(data)

    class Meta:
        abstract = True


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_voter')
    pub_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Review(models.Model):
    title = models.CharField(max_length=160, unique=True)
    content = models.TextField()
    user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_reviewer', on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
