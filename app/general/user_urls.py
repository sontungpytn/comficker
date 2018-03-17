from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.user_index, name='user_all'),
    url(r'^(?P<user_id>[0-9]+)$', views.show_account, name='user_index'),
    url(r'^(?P<user_id>[0-9]+)/edit$', views.user_update, name='user_index'),
]
