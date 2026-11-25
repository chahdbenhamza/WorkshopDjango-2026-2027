"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from EntrepriseApp.views import InscriptionView
from .views import homePage, homepagewithname
from rest_framework.routers import DefaultRouter
from ExpeditionApp.api_views import ExpeditionViewSet
router=DefaultRouter()
router.register('expeditions',ExpeditionViewSet)
urlpatterns = [
    path('users/register/', InscriptionView.as_view(), name='register'),
    path('users/',include('django.contrib.auth.urls')),
    path("", homePage, name='home'),
    path("home/<str:name>", homepagewithname),
    path('admin/', admin.site.urls),
    path('expeditions/', include('ExpeditionApp.urls')),
    path('vehicules/', include('VehiculesApp.urls')),
    path('offres/', include('OffreApp.urls')),
    path('entreprises/', include('EntrepriseApp.urls')),
    path('api/',include(router.urls))
]
