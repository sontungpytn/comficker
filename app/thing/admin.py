from django.contrib import admin
from .models import Thing, Compare, Classify, Comment, Field
# Register your models here.


admin.site.register(Classify)
admin.site.register(Field)
admin.site.register(Thing)
admin.site.register(Compare)
admin.site.register(Comment)
