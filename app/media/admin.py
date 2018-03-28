from django.contrib import admin
from .models import Image, Gallery, GalleryRelationship
# Register your models here.
admin.site.register(Image)
admin.site.register(Gallery)
admin.site.register(GalleryRelationship)
