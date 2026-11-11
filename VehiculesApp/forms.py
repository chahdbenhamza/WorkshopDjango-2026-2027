from django import forms
from .models import Vehicule


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['immatriculation', 'type_vehicule', 'capacite_kg', 'entreprise']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        entreprise_model = Vehicule._meta.get_field('entreprise').remote_field.model
        self.fields['entreprise'].queryset = entreprise_model.objects.filter(
            type_entreprise='transporteur'
        )