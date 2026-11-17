from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Expedition
from .forms import ExpeditionForm

# =====================================================================
# ANCIEN CODE (conservé sous forme de commentaires selon la consigne)
# =====================================================================
# def liste_expeditions(request):
#     expeditions = (
#         Expedition.objects
#         .filter(statut='publiee')
#         .select_related('entreprise')
#         .order_by('-created_at')
#         )
#     return render(request, 'expeditions/liste.html', {'expeditions': expeditions})
#
# def detail_expedition(request, reference):
#     expedition = get_object_or_404(Expedition, reference=reference)
#     offres = (
#         expedition.offre_set
#         .select_related('transporteur', 'vehicule')
#         .order_by('-date_proposition'))
#     return render(request,'expeditions/detail.html',{'expedition': expedition, 'offres': offres},
# )
#
# class ExpeditionListView(ListView):
#     model=Expedition
#     template_name='expeditions/liste.html'
#     context_object_name='expeditions'
#     def get_queryset(self):
#         return Expedition.objects.filter(statut='publiee').select_related('entreprise').order_by('-created_at')
# =====================================================================


# --- Vues génériques CBV (CRUD) ---

class expeditionsCreateView(CreateView):
    model = Expedition
    template_name = 'expeditions/form.html'
    # fields='__all__'
    form_class = ExpeditionForm
    success_url = reverse_lazy('expeditions:list')


# Alias avec convention de nommage standard
ExpeditionCreateView = expeditionsCreateView


class ListExpeditionView(ListView):
    model = Expedition
    template_name = 'expeditions/liste.html'
    context_object_name = 'expeditions'

    def get_queryset(self):
        return Expedition.objects.filter(statut='publiee').select_related('entreprise').order_by('-created_at')


# Alias pour rétro-compatibilité
ExpeditionListView = ListExpeditionView


class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = 'expeditions/detail.html'
    context_object_name = 'expedition'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offres'] = (
            self.object.offre_set
            .select_related('transporteur', 'vehicule')
            .order_by('-date_proposition')
        )
        return context


class ExpeditionUpdateView(UpdateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expeditions/form.html'
    success_url = reverse_lazy('expeditions:list')


class ExpeditionDeleteView(DeleteView):
    model = Expedition
    # form_class = ExpeditionForm
    template_name = 'expeditions/confirm_delete.html'
    success_url = reverse_lazy('expeditions:list')
    context_object_name = 'expedition'

    def form_valid(self, form):
        messages.success(self.request, f"Expédition {self.object.reference} supprimée.")
        return super().form_valid(form)
