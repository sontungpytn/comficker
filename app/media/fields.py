import base64, uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
# Custom image field - handles base 64 encoded images


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,') # format ~= data:image/X,
            ext = format.split('/')[-1] # guess file extension
            idx = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=idx.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)
