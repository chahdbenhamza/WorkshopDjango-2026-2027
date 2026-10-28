from datetime import timedelta
from decimal import Decimal
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from EntrepriseApp.models import Entreprise
from VehiculesApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre


def get_integrity_report():
    """
    Exécute tous les contrôles d'intégrité métier en utilisant l'ORM Django pur
    (annotate, Count, filter, exclude, distinct - aucune boucle Python de filtrage).
    """
    now = timezone.now()
    seuil_7_jours = now - timedelta(days=7)

    # 1. Offres orphelines
    # Offres 'proposee' ou 'acceptee' dont l'expédition associée n'est plus ni publiée ni attribuée
    offres_orphelines = (
        Offre.objects
        .filter(statut__in=['proposee', 'acceptee'])
        .exclude(expedition__statut__in=['publiee', 'Publiée', 'publiée', 'attribue', 'Attribue', 'attribuee'])
        .select_related('expedition', 'transporteur', 'vehicule')
    )

    # 2. Expéditions bloquées
    # Expéditions au statut publiée créées depuis plus de 7 jours
    expeditions_bloquees = (
        Expedition.objects
        .filter(statut__in=['publiee', 'Publiée', 'publiée'], created_at__lt=seuil_7_jours)
        .select_related('entreprise')
    )

    # 3. Transporteurs sans flotte
    # Entreprises de type transporteur ne possédant aucun véhicule
    transporteurs_sans_flotte = (
        Entreprise.objects
        .filter(type_entreprise='transporteur')
        .annotate(nb_vehicules=Count('vehicules'))
        .filter(nb_vehicules=0)
        .select_related('gerant')
    )

    # 4. Incohérence de disponibilité des véhicules
    # Véhicules marqués disponible=True mais assignés à une offre actuellement 'acceptee'
    vehicules_dispo_incoherente = (
        Vehicule.objects
        .filter(disponibilite=True, offre__statut='acceptee')
        .distinct()
        .select_related('entreprise')
    )

    # 5. Doublons de proposition
    # Transporteurs ayant plus d'une offre 'proposee' sur la même expédition (violation Règle 4)
    groupes_doublons = (
        Offre.objects
        .filter(statut='proposee')
        .values('expedition_id', 'transporteur_id')
        .annotate(total=Count('id'))
        .filter(total__gt=1)
    )
    expedition_ids = [g['expedition_id'] for g in groupes_doublons]
    transporteur_ids = [g['transporteur_id'] for g in groupes_doublons]
    offres_doublons = (
        Offre.objects
        .filter(
            statut='proposee',
            expedition_id__in=expedition_ids,
            transporteur_id__in=transporteur_ids,
        )
        .select_related('expedition', 'transporteur')
    )

    # 6. Incohérence de cascade (détecte directement le piège .update() de EXP-26-00001)
    # Expéditions restées 'publiee' malgré la présence d'une offre 'acceptee'
    expeditions_non_attribuees_avec_acceptation = (
        Expedition.objects
        .filter(statut__in=['publiee', 'Publiée', 'publiée'], offre__statut='acceptee')
        .distinct()
        .select_related('entreprise')
    )

    checks = [
        {
            'id': 1,
            'code': 'OFFRES_ORPHELINES',
            'titre': "Offres orphelines",
            'regle_metier': "Règle métier n°5 (Cycle de vie des expéditions & offres)",
            'description': "Offres aux statuts 'proposee' ou 'acceptee' dont l'expédition n'est plus active (annulée, livrée ou en_cours sans lien cohérent).",
            'scenario_risque': "Une annulation ou clôture brute d'expédition par un script SQL direct (.update(statut='annulée')) sans rejeter ou archiver les offres associées.",
            'count': offres_orphelines.count(),
            'items': offres_orphelines,
            'type_items': 'offres',
        },
        {
            'id': 2,
            'code': 'EXPEDITIONS_BLOQUEES',
            'titre': "Expéditions bloquées (> 7 jours)",
            'regle_metier': "Règle de veille opérationnelle & rotation de fret",
            'description': "Expéditions publiées depuis plus de 7 jours consécutifs sans attribution.",
            'scenario_risque': "Offres absentes ou tarifs non compétitifs sur un corridor particulier ; chargeur ayant abandonné la demande sans la clôturer.",
            'count': expeditions_bloquees.count(),
            'items': expeditions_bloquees,
            'type_items': 'expeditions',
        },
        {
            'id': 3,
            'code': 'TRANSPORTEURS_SANS_FLOTTE',
            'titre': "Transporteurs sans flotte",
            'regle_metier': "Règle de conformité transporteur (flotte minimale requise)",
            'description': "Comptes entreprises enregistrés en 'transporteur' sans aucun véhicule rattaché dans le parc.",
            'scenario_risque': "Création de compte via un script d'intégration partenaire ou suppression de véhicules sans contrôle du solde de véhicules actifs.",
            'count': transporteurs_sans_flotte.count(),
            'items': transporteurs_sans_flotte,
            'type_items': 'entreprises',
        },
        {
            'id': 4,
            'code': 'INCOHERENCE_DISPONIBILITE_VEHICULE',
            'titre': "Incohérence de disponibilité des véhicules",
            'regle_metier': "Règle d'exclusivité d'engagement des véhicules",
            'description': "Véhicules marqués disponible=True alors qu'ils sont engagés dans une offre 'acceptee'.",
            'scenario_risque': "Acceptation d'offres en masse sans basculer l'indicateur véhicule.disponibilite à False via une cascade ORM appropriée.",
            'count': vehicules_dispo_incoherente.count(),
            'items': vehicules_dispo_incoherente,
            'type_items': 'vehicules',
        },
        {
            'id': 5,
            'code': 'DOUBLONS_PROPOSITIONS',
            'titre': "Doublons de propositions d'offres",
            'regle_metier': "Règle métier n°4 (Offre unique par transporteur par expédition)",
            'description': "Un même transporteur a soumis plusieurs offres simultanément 'proposee' sur une seule expédition.",
            'scenario_risque': "Double soumission réseau (retry client sans idempotence) ou injection en masse sans contrainte d'unicité en base.",
            'count': offres_doublons.count(),
            'items': offres_doublons,
            'type_items': 'offres',
        },
        {
            'id': 6,
            'code': 'EXPEDITIONS_NON_ATTRIBUEES_AVEC_ACCEPTEE',
            'titre': "Expéditions non attribuées malgré une offre acceptée (Piège .update())",
            'regle_metier': "Règle métier n°5 (Cascade d'acceptation d'offre)",
            'description': "Expéditions restées 'publiee' alors qu'au moins une offre est 'acceptee' (constat direct de la section VII sur EXP-26-00001).",
            'scenario_risque': "Mise à jour en masse SQL via Offre.objects.filter(...).update(statut='acceptee') contournant les méthodes clean() et save().",
            'count': expeditions_non_attribuees_avec_acceptation.count(),
            'items': expeditions_non_attribuees_avec_acceptation,
            'type_items': 'expeditions',
        },
    ]

    for c in checks:
        c['is_ok'] = (c['count'] == 0)
        c['card_class'] = 'check-card-ok' if c['is_ok'] else 'check-card-alert'

    total_checks = len(checks)
    total_anomalies = sum(c['count'] for c in checks)
    checks_en_alerte = sum(1 for c in checks if c['count'] > 0)
    checks_conformes = total_checks - checks_en_alerte

    return {
        'checks': checks,
        'total_checks': total_checks,
        'total_anomalies': total_anomalies,
        'checks_en_alerte': checks_en_alerte,
        'checks_conformes': checks_conformes,
        'timestamp': now,
    }


def health_check_admin_view(request):
    """
    Vue Django pour le tableau de bord d'intégrité /admin/health-check/
    """
    report = get_integrity_report()
    context = {
        **report,
        'title': "Tableau de bord de contrôle d'intégrité métier",
        'site_header': "Partie Admin — TransConnect",
        'has_permission': True,
    }
    return render(request, 'admin/health_check.html', context)

