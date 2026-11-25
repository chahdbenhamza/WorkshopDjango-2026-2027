from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from  django.views.generic import CreateView,ListView,UpdateView,DeleteView
from .models import Vehicule
from .forms import VehiculeForm
from django.urls import reverse_lazy
class vehiculesCreateView(LoginRequiredMixin, CreateView):
    model=Vehicule
    template_name='vehicules/form.html'
    #fields='__all__'
    form_class=VehiculeForm
    # success_url=reverse_lazy('Vehicules:list')
    success_url=reverse_lazy('vehicules:list')

class ListVehiculeView(LoginRequiredMixin, ListView):
    model=Vehicule
    template_name='vehicules/list.html'
    context_object_name='vehicules'



class VehiculeUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicules/form.html'
    success_url = reverse_lazy('vehicules:list')

class VehiculeDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicule
    # form_class = VehiculeForm
    template_name = 'vehicules/confirm_delete.html'
    success_url = reverse_lazy('vehicules:list')
    context_object_name='vehicule'
    def form_valid(self, form):
        messages.success(self.request, f"Véhicule {self.object.immatriculation} supprimé.")
        return super().form_valid(form)
