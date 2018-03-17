from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.APIListImage.as_view(), name='list'),
    url(r'^create/$', views.APICreateImage.as_view(), name='create'),
    url(r'^gallery/$', views.APIListAlbum.as_view(), name='list_gallery'),
    url(r'^gallery/create/$', views.APICreateGallery.as_view(), name='create_gallery'),
    url(r'^gallery/(?P<id>[\w-]+)/edit/$', views.APIUpdateGallery.as_view(), name='update_gallery'),
    url(r'^(?P<id>[\w-]+)/$', views.APIDetailImage.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$', views.APIUpdateImage.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/delete/$', views.APIDeleteImage.as_view(), name='delete'),

]
