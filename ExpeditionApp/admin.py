from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from OffreApp.models import Offre
from .models import Expedition


class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [
            ('oui', 'Oui'),
            ('non', 'Non'),
        ]

    def queryset(self, request, queryset):
        statuts_ouverts = ['publiee', 'Publiée', 'publiée']
        now = timezone.now()
        if self.value() == 'oui':
            return queryset.filter(statut__in=statuts_ouverts, date_souhaitée__lt=now)
        elif self.value() == 'non':
            return queryset.exclude(statut__in=statuts_ouverts, date_souhaitée__lt=now)
        return queryset


class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    inlines = [OffreInline]
    list_display = (
        'reference',
        'entreprise',
        'ville_depart',
        'ville_arrive',
        'poid_kg',
        'date_souhaitée',
        'statut_colore',
    )
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    search_fields = ('reference', 'entreprise__raison_sociale', 'ville_depart', 'ville_arrive')
    autocomplete_fields = ('entreprise',)
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'date_souhaitée'

    fieldsets = (
        ('Trajet', {
            'fields': ('reference', 'ville_depart', 'ville_arrive', 'description')
        }),
        ('Détails & Statut', {
            'fields': ('entreprise', 'poid_kg', 'date_souhaitée', 'statut')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('reference', 'created_at', 'updated_at')
    actions = ['cloturer_expeditions']

    @admin.display(description='Statut')
    def statut_colore(self, obj):
        couleurs = {
            'publiee': '#0275D8',
            'Publiée': '#0275D8',
            'publiée': '#0275D8',
            'attribue': '#5CB85C',
            'Attribue': '#5CB85C',
            'attribuee': '#5CB85C',
            'en_cours': '#F0AD4E',
            'En_cours': '#F0AD4E',
            'livrée': '#28A745',
            'Livrée': '#28A745',
            'Annulée': '#D9534F',
            'annulée': '#D9534F',
        }
        statut_display = obj.get_statut_display() if hasattr(obj, 'get_statut_display') else obj.statut
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;font-weight:600;">{}</span>',
            couleurs.get(obj.statut, '#6c757d'),
            statut_display,
        )

    @admin.action(description="Clôturer les expéditions sélectionnées")
    def cloturer_expeditions(self, request, queryset):
        ciblees = queryset.filter(statut__in=['en_cours', 'En_cours'])
        ignorees = queryset.exclude(statut__in=['en_cours', 'En_cours']).count()
        succes = 0
        erreurs = []

        for exp in ciblees:
            exp.statut = 'livrée'
            try:
                exp.full_clean()
                exp.save()
                succes += 1
            except ValidationError as err:
                erreurs.append(f"{exp.reference}: {err}")

        if succes:
            self.message_user(
                request,
                f"{succes} expédition(s) clôturée(s) avec succès.",
                messages.SUCCESS,
            )
        if ignorees:
            self.message_user(
                request,
                f"{ignorees} expédition(s) ignorée(s) (seules les expéditions 'en_cours' peuvent être clôturées).",
                messages.WARNING,
            )
        for err in erreurs:
            self.message_user(request, err, messages.ERROR)

    # Alias pour compatibilité
    make_it_delivered = cloturer_expeditions
