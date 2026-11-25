from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Entreprise
from .forms import EntrepriseForm, InscriptionForm

# =====================================================================
# ANCIEN CODE (conservé sous forme de commentaires selon la consigne)
# =====================================================================
# def liste_entreprises(request):
#     entreprises = Entreprise.objects.select_related('gerant').all()
#     return render(request, 'entreprises/list.html', {'entreprises': entreprises})
# =====================================================================


# --- Vues génériques CBV (CRUD) ---

class InscriptionView(CreateView):
    form_class = InscriptionForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('entreprises:create')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class entrepriseCreateView(LoginRequiredMixin, CreateView):
    model = Entreprise
    template_name = 'entreprises/form.html'
    form_class = EntrepriseForm
    success_url = reverse_lazy('entreprises:list')

    def form_valid(self, form):
        form.instance.gerant = self.request.user
        return super().form_valid(form)


# Alias avec convention de nommage standard
EntrepriseCreateView = entrepriseCreateView


class ListEntrepriseView(LoginRequiredMixin, ListView):
    model = Entreprise
    template_name = 'entreprises/list.html'
    context_object_name = 'entreprises'

    def get_queryset(self):
        return Entreprise.objects.select_related('gerant').order_by('-created_at')


class EntrepriseDetailView(LoginRequiredMixin, DetailView):
    model = Entreprise
    template_name = 'entreprises/detail.html'
    context_object_name = 'entreprise'


class EntrepriseUpdateView(LoginRequiredMixin, UpdateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'entreprises/form.html'
    success_url = reverse_lazy('entreprises:list')


class EntrepriseDeleteView(LoginRequiredMixin, DeleteView):
    model = Entreprise
    # form_class = EntrepriseForm
    template_name = 'entreprises/confirm_delete.html'
    success_url = reverse_lazy('entreprises:list')
    context_object_name = 'entreprise'

    def form_valid(self, form):
        messages.success(self.request, f"Entreprise {self.object.raison_sociale} supprimée.")
        return super().form_valid(form)
