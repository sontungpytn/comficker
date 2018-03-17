from __future__ import unicode_literals
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.db import models
import os
from uuid import uuid4
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
# Create your models here.


def path_and_rename(instance, filename):
    upload_to = 'site_images/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class ContentType(models.Model):
    name = models.CharField(max_length=160, unique=True)
    slug = models.CharField(max_length=160, unique=True)
    description = models.TextField(null=True)
    image = VersatileImageField('Path', upload_to=path_and_rename, ppoi_field='path_ppoi')
    path_ppoi = PPOIField()

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(ContentType, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = VersatileImageField('Path', upload_to=path_and_rename, ppoi_field='path_ppoi')
    extra = JSONField()

    path_ppoi = PPOIField()

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(UserProfile, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class Definition(models.Model):
    name = models.CharField(max_length=80)
    content = models.TextField()
