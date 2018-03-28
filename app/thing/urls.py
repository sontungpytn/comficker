from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', views.thing_show, name='classify'),
    url(r'^(?P<slug>[\w-]+)/(?P<first>[\w-]+)-and-(?P<second>[\w-]+)', views.thing_compare, name='compare'),

    # url(r'^$', views.media_index, name='index_media'),
    # url(r'^all$', views.media_all, name='all_media'),
    # url(r'^upload$', views.media_upload, name='create_media'),
    # url(r'^(?P<id>[0-9]+)/edit$', views.media_edit, name='edit_media'),
    # url(r'^(?P<id>[0-9]+)/delete$', views.media_delete, name='delete_media'),
    # url(r'^(?P<id>[0-9]+)$', views.media_show, name='show_media'),
    # url(r'^gallery$', views.gallery_index, name='index_gallery'),
    # url(r'^gallery/create$', views.gallery_add, name='create_gallery'),
    # url(r'^gallery/(?P<slug>[\w-]+)$', views.gallery_show, name='show_gallery'),
    # url(r'^gallery/(?P<slug>[\w-]+)/edit$', views.gallery_edit, name='edit_gallery'),
    # url(r'^gallery/(?P<slug>[\w-]+)/delete$', views.gallery_delete, name='delete_gallery'),
]
