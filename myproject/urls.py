"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from .views import homePage, homepagewithname

urlpatterns = [
    path("", homePage, name='home'),
    path("home/<str:name>", homepagewithname),
    path('admin/', admin.site.urls),
    path('expeditions/', include('ExpeditionApp.urls')),
    path('vehicules/', include('VehiculesApp.urls')),
    path('offres/', include('OffreApp.urls')),
    path('entreprises/', include('EntrepriseApp.urls')),
]
