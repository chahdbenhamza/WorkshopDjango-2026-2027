from django.urls import path
from . import views

app_name = 'expeditions'

urlpatterns = [
    # --- Ancien code commenté ---
    # path("", views.liste_expeditions, name="liste_expeditions"),
    # path("<str:reference>/", views.detail_expedition, name="detail"),

    # --- Nouvelles routes CRUD ---
    path("", views.ListExpeditionView.as_view(), name="liste_expeditions"),
    path("list/", views.ListExpeditionView.as_view(), name="list"),
    path("create/", views.expeditionsCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.ExpeditionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ExpeditionDeleteView.as_view(), name="delete"),
    path("<str:reference>/", views.ExpeditionDetailView.as_view(), name="detail"),
]
