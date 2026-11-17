from django import forms
from .models import Entreprise, Utilisateur


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['raison_sociale', 'matricule_fiscal', 'type_entreprise', 'adresse', 'gerant']
        widgets = {
            'adresse': forms.TextInput(attrs={'placeholder': "Au moins 20 caractères..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permettre de sélectionner les utilisateurs
        self.fields['gerant'].queryset = Utilisateur.objects.all()

