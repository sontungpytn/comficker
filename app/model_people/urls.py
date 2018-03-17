from django.conf.urls import url

from . import views

prefix = 'people_'
urlpatterns = [
    url(r'^$', views.ModelList.as_view(), name=prefix + 'index'),
    url(r'^create/$', views.ModelCreate.as_view(), name=prefix + 'create'),
    url(r'^compare/$', views.ModelCompareClassify.as_view(), name=prefix + 'compare_classify'),
    url(r'^compare/(?P<first>[\w-]+)-and-(?P<second>[\w-]+)$', views.ModelCompareList.as_view(),
        name=prefix + 'compare_list'),
    url(r'^filter$', views.ModelClassify.as_view(), name=prefix + 'classify'),
    url(r'^filter/(?P<field>[\w-]+)$', views.ModelField.as_view(), name=prefix + 'field'),
    url(r'^filter/(?P<field>[\w-]+)/(?P<value>.*)', views.Filter.as_view(), name=prefix + 'filter'),
    url(r'^(?P<model_slug>[\w-]+)/$', views.ModelDetail.as_view(), name=prefix + 'show'),
    url(r'^(?P<model_slug>[\w-]+)/edit', views.ModelEdit.as_view(), name=prefix + 'update'),
    url(r'^(?P<model_slug>[\w-]+)/delete$', views.ModelDelete.as_view(), name=prefix + 'delete'),
    url(r'^(?P<model_slug>[\w-]+)/like', views.ModelVote.as_view(), name=prefix + 'vote'),
    url(r'^(?P<first>[\w-]+)-and-(?P<second>[\w-]+)', views.ModelCompareDetail.as_view(),
        name=prefix + 'compare_detail'),
]
