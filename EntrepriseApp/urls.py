from django.urls import path
from .views import *

app_name = 'entreprises'

urlpatterns = [
    # --- Routes CRUD CBV ---
    path('', ListEntrepriseView.as_view(), name='list'),
    path('list/', ListEntrepriseView.as_view(), name='list_alias'),
    path('create/', entrepriseCreateView.as_view(), name='create'),
    path('<int:pk>/', EntrepriseDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', EntrepriseUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', EntrepriseDeleteView.as_view(), name='delete'),
]

