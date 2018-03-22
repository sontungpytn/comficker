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
from . import views
from app.model_food.api import views as model_food_views
from app.model_vehicle.api import views as model_vehicle_views
from app.model_people.api import views as model_people_views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'food/classify', model_food_views.ClassifyViewSet)
router.register(r'vehicle/classify', model_vehicle_views.ClassifyViewSet)
router.register(r'people/classify', model_people_views.ClassifyViewSet)
router.register(r'vehicle', model_vehicle_views.ModelViewSet)
router.register(r'food', model_food_views.ModelViewSet)
router.register(r'people', model_people_views.ModelViewSet)


urlpatterns = [
    url(r'^$', views.welcome, name='home'),
    url(r'^api/', include(router.urls)),
    url(r'^member/', include('registration.backends.hmac.urls')),
    url(r'^member/', include(('app.general.user_urls', 'member'), namespace='user')),
    url(r'^admin/', admin.site.urls),
    url(r'^food/', include(('app.model_food.urls', 'food'), namespace='food')),
    url(r'^vehicle/', include(('app.model_vehicle.urls', 'vehicle'), namespace='vehicle')),
    url(r'^people/', include(('app.model_people.urls', 'people'), namespace='people')),
    url(r'^media/', include(('app.media.urls', 'media'), namespace='media')),
    url(r'^api/photos/', include(('app.media.api.urls', 'media'), namespace='images-api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.error_404
handler500 = views.error_500
