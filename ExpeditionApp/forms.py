from django import forms
from .models import Expedition
from EntrepriseApp.models import Entreprise


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = [
            'ville_depart',
            'ville_arrive',
            'date_souhaitée',
            'poid_kg',
            'statut',
            'entreprise',
            'description',
        ]
        widgets = {
            'date_souhaitée': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entreprise'].queryset = Entreprise.objects.filter(
            type_entreprise='chargeur'
        )

