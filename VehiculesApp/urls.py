from django.urls import path
from .views import *
app_name='vehicules'
urlpatterns=[
    path('create/',vehiculesCreateView.as_view(),name='create'),
    path('list/',ListVehiculeView.as_view(),name='list'),
    path('<int:pk>/update/',VehiculeUpdateView.as_view(),name='update'),
    path('<int:pk>/delete/',VehiculeDeleteView.as_view(),name='delete'),
]