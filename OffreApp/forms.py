from django import forms
from .models import Offre
from EntrepriseApp.models import Entreprise
from VehiculesApp.models import Vehicule
from ExpeditionApp.models import Expedition


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transporteur'].queryset = Entreprise.objects.filter(
            type_entreprise='transporteur'
        )
        self.fields['expedition'].queryset = Expedition.objects.filter(
            statut__in=['publiee', 'Publiée', 'publiée']
        )

