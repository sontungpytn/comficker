"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from app.thing.api import views as thing_api_views
from app.thing import models
from rest_framework.routers import DefaultRouter
from .sitemaps import StaticViewSitemap
from . import views
from django.urls import path

sitemaps = {
    'static': StaticViewSitemap,
}

map_compare = {
    'queryset': models.Compare.objects.all().order_by('-id'),
    'date_field': 'created_date',
}

map_category = {
    'queryset': models.Classify.objects.all().order_by('-id'),
}

map_thing = {
    'queryset': models.Thing.objects.all().order_by('-id'),
}

router = DefaultRouter()
router.register(r'thing', thing_api_views.ThingViewSet)
router.register(r'field', thing_api_views.FieldViewSet)
router.register(r'classify', thing_api_views.ClassifyFieldViewSet)

urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^robots\.txt', include('robots.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-compare.xml', sitemap, {'sitemaps': {'blog': GenericSitemap(map_compare, priority=0.6)}},
         name='sitemap_compare'),
    path('sitemap-category.xml', sitemap, {'sitemaps': {'blog': GenericSitemap(map_category, priority=0.6)}},
         name='sitemap_category'),
    path('sitemap-thing.xml', sitemap, {'sitemaps': {'blog': GenericSitemap(map_thing, priority=0.6)}},
         name='sitemap_thing'),
    url(r'^$', views.welcome, name='home'),
    url(r'^api/', include(router.urls)),
    url(r'^member/', include('registration.backends.hmac.urls')),
    url(r'^member/', include(('app.general.user_urls', 'member'), namespace='user')),
    url(r'^admin/', admin.site.urls),
    url(r'^media/', include(('app.media.urls', 'media'), namespace='media')),
    url(r'^api/photos/', include(('app.media.api.urls', 'media'), namespace='images-api')),
    url(r'^', include(('app.thing.urls', 'thing'), namespace='thing')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.error_404
handler500 = views.error_500
