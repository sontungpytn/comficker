from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Model)
admin.site.register(models.Classify)
admin.site.register(models.Review)
admin.site.register(models.Vote)
admin.site.register(models.Field)
