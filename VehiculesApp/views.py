from django.shortcuts import render
from django.contrib import messages
from  django.views.generic import CreateView,ListView,UpdateView,DeleteView
from .models import Vehicule
from .forms import VehiculeForm
from django.urls import reverse_lazy
class vehiculesCreateView(CreateView):
    model=Vehicule
    template_name='vehicules/form.html'
    #fields='__all__'
    form_class=VehiculeForm
    success_url=reverse_lazy('Vehicules:list')

class ListVehiculeView(ListView):
    model=Vehicule
    template_name='vehicules/list.html'
    context_object_name='vehicules'



class VehiculeUpdateView(UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicules/form.html'
    success_url = reverse_lazy('vehicules:list')

class VehiculeDeleteView(DeleteView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicules/confirm_delete.html'
    success_url = reverse_lazy('vehicules:list')
    context_object_name='vehicule'
    def form_valid(self, form):
        messages.success(self.request, f"Véhicule {self.object.immatriculation} supprimé.")
        return super().form_valid(form)
