from django.urls import path

from . import views
app_name='expeditions'
urlpatterns=[
    #path("", views.liste_expeditions, name="liste_expeditions"),
    path("", views.ExpeditionListView.as_view(), name="liste_expeditions"),
    #path("<str:reference>/", views.detail_expedition, name="detail"),
    path("<str:reference>/", views.ExpeditionDetailView.as_view(), name="detail"),
]