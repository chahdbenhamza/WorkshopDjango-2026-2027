from django.urls import path
from .views import *

app_name = 'offres'

urlpatterns = [
    # --- Routes CRUD CBV ---
    path('', ListOffreView.as_view(), name='list'),
    path('list/', ListOffreView.as_view(), name='list_alias'),
    path('create/', offresCreateView.as_view(), name='create'),
    path('<int:pk>/', OffreDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', OffreUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', OffreDeleteView.as_view(), name='delete'),
]

