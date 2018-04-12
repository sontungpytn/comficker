from django.contrib import admin
from .models import Thing, Compare, Classify, Comment, Field
# Register your models here.


class ThingAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_filter = ('is_edited', 'classify')
    search_fields = ['name']


class ClassifyAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_filter = ('allow_foreign_compare', 'parent')
    search_fields = ['name']


class FieldAdmin(admin.ModelAdmin):
    list_filter = ('classify', 'parent')
    search_fields = ['name']


admin.site.register(Classify, ClassifyAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Thing, ThingAdmin)
admin.site.register(Compare)
admin.site.register(Comment)
