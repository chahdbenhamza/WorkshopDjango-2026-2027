from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Offre
from .forms import OffreForm

# =====================================================================
# ANCIEN CODE (conservé sous forme de commentaires selon la consigne)
# =====================================================================
# def liste_offres(request):
#     offres = Offre.objects.select_related('expedition', 'transporteur', 'vehicule').all()
#     return render(request, 'offres/list.html', {'offres': offres})
# =====================================================================


# --- Vues génériques CBV (CRUD) ---

class offresCreateView(LoginRequiredMixin, CreateView):
    model = Offre
    template_name = 'offres/form.html'
    # fields='__all__'
    form_class = OffreForm
    success_url = reverse_lazy('offres:list')


# Alias avec convention de nommage standard
OffreCreateView = offresCreateView


class ListOffreView(LoginRequiredMixin, ListView):
    model = Offre
    template_name = 'offres/list.html'
    context_object_name = 'offres'

    def get_queryset(self):
        return Offre.objects.select_related('expedition', 'transporteur', 'vehicule').order_by('-created_at')


class OffreDetailView(LoginRequiredMixin, DetailView):
    model = Offre
    template_name = 'offres/detail.html'
    context_object_name = 'offre'


class OffreUpdateView(LoginRequiredMixin, UpdateView):
    model = Offre
    form_class = OffreForm
    template_name = 'offres/form.html'
    success_url = reverse_lazy('offres:list')


class OffreDeleteView(LoginRequiredMixin, DeleteView):
    model = Offre
    # form_class = OffreForm
    template_name = 'offres/confirm_delete.html'
    success_url = reverse_lazy('offres:list')
    context_object_name = 'offre'

    def form_valid(self, form):
        messages.success(self.request, f"Offre #{self.object.id} supprimée.")
        return super().form_valid(form)
