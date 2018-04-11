from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create/$', views.thing_create, name='thing_create'),
    url(r'^(?P<classify_slug>[\w-]+)/item/(?P<thing_slug>[\w-]+)/$', views.thing, name='thing_detail'),
    url(r'^(?P<classify_slug>[\w-]+)/item/(?P<thing_slug>[\w-]+)/edit$', views.thing_edit, name='thing_edit'),
    url(r'^(?P<slug>[\w-]+)/$', views.thing_show, name='thing_show'),
    url(r'^(?P<slug>[\w-]+)/(?P<first>[\w-]+)-and-(?P<second>[\w-]+)', views.thing_compare, name='compare'),
]
