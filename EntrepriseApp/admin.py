from django.contrib import admin
from django.urls import path

from VehiculesApp.models import Vehicule
from .health_check import health_check_admin_view
from .models import Utilisateur, Entreprise

# --- Configuration de l'image de marque (Branding) ---
admin.site.site_header = "Partie Admin — TransConnect"
admin.site.site_title = "TransConnect"
admin.site.index_title = "Tableau de bord des opérations TransConnect"


# --- Surcharge de get_urls() sur le site admin pour le tableau de bord d'intégrité ---
_default_admin_get_urls = admin.site.get_urls


def _custom_admin_get_urls():
    custom_urls = [
        path('health-check/', admin.site.admin_view(health_check_admin_view), name='health_check'),
    ]
    return custom_urls + _default_admin_get_urls()


admin.site.get_urls = _custom_admin_get_urls


@admin.register(Utilisateur)
class AdminUtilisateur(admin.ModelAdmin):
    list_display = ('username', 'user_id', 'first_name', 'last_name', 'roles', 'email', 'is_staff', 'is_active')
    list_filter = ('roles', 'is_staff', 'is_active')
    list_editable = ('last_name', 'first_name')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telephone')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Informations utilisateur', {
            'fields': ('roles', 'email', 'telephone', 'is_staff', 'is_active')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponibilite')


@admin.register(Entreprise)
class AdminEntreprise(admin.ModelAdmin):
    inlines = [VehiculeInline]
    list_display = ('matricule_fiscal', 'raison_sociale', 'type_entreprise', 'gerant', 'adresse')
    list_filter = ('type_entreprise',)
    list_editable = ('adresse',)
    search_fields = ('raison_sociale', 'matricule_fiscal')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Informations générales', {
            'fields': ('matricule_fiscal', 'raison_sociale')
        }),
        ('Détails entreprise', {
            'fields': ('type_entreprise', 'gerant', 'adresse')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
