from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField, PPOIField
import os
from uuid import uuid4
import datetime
# Create your models here.


def path_and_rename(instance, filename):
    now = datetime.datetime.now()
    upload_to = 'images/' + str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Image(models.Model):
    title = models.CharField(max_length=160, unique=True)
    description = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = VersatileImageField(
        'Path',
        upload_to=path_and_rename,
        ppoi_field='path_ppoi'
    )
    path_ppoi = PPOIField()
    pub_date = models.DateTimeField('date published')

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.path.storage, self.path.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class Gallery(models.Model):
    title = models.CharField(max_length=160, unique=True)
    description = models.TextField(null=True)
    featured = models.ForeignKey(Image)
    slug = models.CharField(max_length=160, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')

    def list_images(self):
        relations = GalleryRelationship.objects.filter(gallery=self)
        return relations


class GalleryRelationship(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='photos', on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')

    class Meta:
        db_table = 'media_gallery_relationship'
        unique_together = ('gallery', 'image')
        ordering = ['id']


def decode_base64_file(data, prefix='photo_'):

    def get_file_extension(file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

    from django.core.files.base import ContentFile
    import base64
    import six
    import uuid

    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            TypeError('invalid_image')

        # Generate file name:
        file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
        # Get the file name extension:
        file_extension = get_file_extension(file_name, decoded_file)

        complete_file_name = prefix + "%s.%s" % (file_name, file_extension, )

        return ContentFile(decoded_file, name=complete_file_name)