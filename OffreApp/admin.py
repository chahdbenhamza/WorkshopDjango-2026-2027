import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Offre


@admin.action(description="Exporter la sélection en CSV")
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([
            offre.expedition.reference,
            offre.transporteur.raison_sociale,
            offre.prix,
            offre.statut,
        ])
    return response


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        'expedition',
        'transporteur',
        'vehicule',
        'prix',
        'delai_jours',
        'statut_colore',
        'date_proposition',
    )
    list_filter = ('statut', 'transporteur')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'date_proposition'

    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    readonly_fields = ('date_proposition', 'created_at', 'updated_at', 'statut_colore')

    fieldsets = (
        ('Détails de l\'offre', {
            'fields': ('expedition', 'transporteur', 'vehicule')
        }),
        ('Conditions', {
            'fields': ('prix', 'delai_jours')
        }),
        ('Suivi', {
            'fields': ('statut_colore', 'date_proposition', 'created_at', 'updated_at')
        }),
    )

    actions = [exporter_offres_csv]

    @admin.display(description='Statut')
    def statut_colore(self, obj):
        if not obj or not obj.statut:
            return '-'
        couleurs = {
            'proposee': '#F0AD4E',
            'acceptee': '#5CB85C',
            'refusee': '#D9534F',
            'retiree': '#777777',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;font-weight:600;">{}</span>',
            couleurs.get(obj.statut, '#999'),
            obj.get_statut_display(),
        )

    def get_readonly_fields(self, request, obj=None):
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base
