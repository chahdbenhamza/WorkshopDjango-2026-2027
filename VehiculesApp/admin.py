from django.contrib import admin
from .models import Vehicule


@admin.register(Vehicule)
class AdminVehicule(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'entreprise', 'disponibilite', 'capacite_kg')
    list_filter = ('type_vehicule', 'disponibilite', 'entreprise')
    list_editable = ('disponibilite',)
    search_fields = ('immatriculation', 'type_vehicule', 'entreprise__raison_sociale')
    autocomplete_fields = ('entreprise',)
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Informations véhicule', {
            'fields': ('immatriculation', 'type_vehicule', 'capacite_kg')
        }),
        ('Rattachement & Disponibilité', {
            'fields': ('entreprise', 'disponibilite')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
