from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Entreprise, Utilisateur


class InscriptionForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'email', 'telephone')
        labels = {
            'username': "Nom d'utilisateur",
            'email': 'Adresse e-mail (Gmail)',
            'telephone': 'Téléphone (facultatif)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'telephone': forms.TelInput(attrs={'autocomplete': 'tel'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password1'].help_text = ''
        self.fields['password2'].label = 'Confirmer le mot de passe'
        self.fields['password2'].help_text = ''


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['raison_sociale', 'matricule_fiscal', 'type_entreprise', 'adresse']
        widgets = {
            'adresse': forms.TextInput(attrs={'placeholder': "Au moins 20 caractères..."}),
        }


