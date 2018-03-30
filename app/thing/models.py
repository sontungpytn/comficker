from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models

from app.media.models import Image, Gallery


# Create your models here.


class Classify(models.Model):
    name = models.CharField(max_length=20)
    slug = models.CharField(max_length=60)
    image = models.ForeignKey(Image, blank=True, on_delete=models.SET_NULL, related_name='classify_image', null=True)
    allow_foreign_compare = models.BooleanField(default=True)
    description = models.CharField(max_length=120, blank=True)
    parent = models.ForeignKey("self", related_name='parent_classify', on_delete=models.SET_NULL, blank=True, null=True)
    created_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def child(self):
        data = []
        for child in Classify.objects.filter(parent=self).order_by('name'):
            data.append(child)
            data = data + child.child()
        return data

    def parents(self):
        data = []
        if self.parent is not None:
            data.append(self.parent)
            data= data + self.parent.parents()
        return data

    def master_parent(self):
        for parent in self.parents():
            if parent.parent is None:
                return parent
        return self

    def fields(self):
        data = []
        for field in Field.objects.filter(classify=self).order_by('name'):
            if field.parent is None:
                data.append(field)
        return data

    def things(self):
        return Thing.objects.filter(classify=self).order_by('name')


class Field(models.Model):
    name = models.CharField(max_length=20)
    slug = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    classify = models.ForeignKey(Classify, on_delete=models.CASCADE, related_name='field_classify')
    parent = models.ForeignKey("self", related_name='parent_field', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    def childs(self):
        return Field.objects.filter(parent=self)


class Thing(models.Model):
    name = models.CharField(max_length=60)
    slug = models.CharField(max_length=60)
    photos = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    data = JSONField(blank=True)
    classify = models.ForeignKey(Classify, blank=True, on_delete=models.SET_NULL, related_name='thing_classify',
                                 null=True, default=None)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thing_creator')
    is_edited = models.BooleanField(default=True, blank=True)
    created_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Compare(models.Model):
    first = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='first_compare')
    second = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='second_compare')
    data = JSONField(blank=True, null=True, default=None)
    slug = models.CharField(max_length=120)
    created_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.first.name + " and " + self.second.name


class Comment(models.Model):
    compare = models.ForeignKey(Compare, on_delete=models.CASCADE, related_name='comment_thing')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    content = models.TextField()
    created_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.username + " comment on " + self.compare.slug


class Vote(models.Model):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name='vote_thing')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_user')
    created_date = models.DateField(auto_now=True)
