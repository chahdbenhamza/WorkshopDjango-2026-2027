from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre


class Command(BaseCommand):
    help = "Génère le jeu de données de test pour la démonstration de l'atelier Admin (EXP-26-00001 et EXP-26-00002)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initialisation du jeu de données seed_demo..."))

        def get_or_create_user(username, email, roles, phone, first_name, last_name):
            u = Utilisateur.objects.filter(username=username).first()
            if not u:
                u = Utilisateur(
                    username=username,
                    email=email,
                    telephone=phone,
                    roles=roles,
                    first_name=first_name,
                    last_name=last_name,
                )
                u.set_password("Admin1234!")
                u.save()
            return u

        with transaction.atomic():
            # 1. Utilisateurs
            u_chargeur = get_or_create_user(
                "chargeur_seed", "chargeur.seed@gmail.com", "chargeur", "+21620000001", "Sami", "Chargeur"
            )
            u_transp1 = get_or_create_user(
                "transp1_seed", "transp1.seed@gmail.com", "transporteur", "+21620000002", "Karim", "Express"
            )
            u_transp2 = get_or_create_user(
                "transp2_seed", "transp2.seed@gmail.com", "transporteur", "+21620000003", "Nader", "Logistique"
            )

            # 2. Entreprises
            ent_chargeur = Entreprise.objects.filter(gerant=u_chargeur).first()
            if not ent_chargeur:
                ent_chargeur = Entreprise.objects.create(
                    gerant=u_chargeur,
                    raison_sociale="Agro Alimentaire Tunisie SA",
                    matricule_fiscal="1111111AAM001",
                    type_entreprise="chargeur",
                    adresse="Zone Industrielle Ben Arous, 2013 Ben Arous, Tunisie",
                )

            ent_transp1 = Entreprise.objects.filter(gerant=u_transp1).first()
            if not ent_transp1:
                ent_transp1 = Entreprise.objects.create(
                    gerant=u_transp1,
                    raison_sociale="Trans Express Tunisie",
                    matricule_fiscal="2222222BAM002",
                    type_entreprise="transporteur",
                    adresse="Route de la Marsa km 7, 2045 Tunis, Tunisie",
                )

            ent_transp2 = Entreprise.objects.filter(gerant=u_transp2).first()
            if not ent_transp2:
                ent_transp2 = Entreprise.objects.create(
                    gerant=u_transp2,
                    raison_sociale="Maghreb Fret Logistics",
                    matricule_fiscal="3333333CAM003",
                    type_entreprise="transporteur",
                    adresse="Avenue Habib Bourguiba, 4000 Sousse, Tunisie",
                )

            # 3. Véhicules (Camionnette : 0 à 1500 kg)
            v1 = Vehicule.objects.filter(immatriculation="199 TUN 1111").first()
            if not v1:
                v1 = Vehicule.objects.create(
                    immatriculation="199 TUN 1111",
                    type_vehicule="camionnette",
                    capacite_kg=1200,
                    disponibilite=True,
                    entreprise=ent_transp1,
                )

            v2 = Vehicule.objects.filter(immatriculation="205 TUN 2222").first()
            if not v2:
                v2 = Vehicule.objects.create(
                    immatriculation="205 TUN 2222",
                    type_vehicule="camionnette",
                    capacite_kg=1400,
                    disponibilite=True,
                    entreprise=ent_transp2,
                )

            # 4. Expéditions EXP-26-00001 et EXP-26-00002
            date_future = timezone.now() + timezone.timedelta(days=4)

            # Expédition 1
            exp1 = Expedition.objects.filter(reference="EXP-26-00001").first()
            if not exp1:
                exp1 = Expedition(
                    entreprise=ent_chargeur,
                    ville_depart="Tunis",
                    ville_arrive="Sfax",
                    date_souhaitée=date_future,
                    poid_kg=Decimal("450.00"),
                    statut="publiee",
                    description="Transport de pièces détachées",
                )
                exp1.save()
                Expedition.objects.filter(pk=exp1.pk).update(reference="EXP-26-00001", statut="publiee")
                exp1.refresh_from_db()
            else:
                Expedition.objects.filter(pk=exp1.pk).update(statut="publiee")
                exp1.refresh_from_db()

            # Nettoyer et réinitialiser les 2 offres pour exp1
            Offre.objects.filter(expedition=exp1).delete()
            Offre.objects.create(
                expedition=exp1,
                transporteur=ent_transp1,
                vehicule=v1,
                prix=Decimal("350.00"),
                delai_jours=2,
                statut="proposee",
            )
            Offre.objects.create(
                expedition=exp1,
                transporteur=ent_transp2,
                vehicule=v2,
                prix=Decimal("320.00"),
                delai_jours=3,
                statut="proposee",
            )

            # Expédition 2
            exp2 = Expedition.objects.filter(reference="EXP-26-00002").first()
            if not exp2:
                exp2 = Expedition(
                    entreprise=ent_chargeur,
                    ville_depart="Bizerte",
                    ville_arrive="Sousse",
                    date_souhaitée=date_future,
                    poid_kg=Decimal("400.00"),
                    statut="publiee",
                    description="Livraison de composants électroniques",
                )
                exp2.save()
                Expedition.objects.filter(pk=exp2.pk).update(reference="EXP-26-00002", statut="publiee")
                exp2.refresh_from_db()
            else:
                Expedition.objects.filter(pk=exp2.pk).update(statut="publiee")
                exp2.refresh_from_db()

            # Nettoyer et réinitialiser les 2 offres pour exp2
            Offre.objects.filter(expedition=exp2).delete()
            Offre.objects.create(
                expedition=exp2,
                transporteur=ent_transp1,
                vehicule=v1,
                prix=Decimal("450.00"),
                delai_jours=1,
                statut="proposee",
            )
            Offre.objects.create(
                expedition=exp2,
                transporteur=ent_transp2,
                vehicule=v2,
                prix=Decimal("410.00"),
                delai_jours=2,
                statut="proposee",
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Un message de succès confirme la création de deux expéditions : EXP-26-00001 et EXP-26-00002."
            )
        )

