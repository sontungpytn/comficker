from django.contrib import admin
from .models import ContentType, UserProfile, Definition
# Register your models here.


admin.site.register(ContentType)
admin.site.register(UserProfile)
admin.site.register(Definition)
