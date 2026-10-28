from datetime import timedelta
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from EntrepriseApp.models import Utilisateur, Entreprise
from ExpeditionApp.models import Expedition
from OffreApp.admin import OffreAdmin, exporter_offres_csv
from OffreApp.models import Offre
from VehiculesApp.models import Vehicule


class OffreAdminTests(TestCase):
    def setUp(self):
        self.user_chargeur = Utilisateur(
            username="chargeur_u",
            email="chargeur.u@gmail.com",
            roles="chargeur",
        )
        self.user_chargeur.set_password("Admin1234!")
        self.user_chargeur.save()

        self.chargeur = Entreprise.objects.create(
            gerant=self.user_chargeur,
            raison_sociale="Chargeur SA",
            matricule_fiscal="1234567AAM222",
            type_entreprise="chargeur",
            adresse="Avenue de Carthage, 1000 Tunis, Tunisie",
        )

        self.user_transp = Utilisateur(
            username="transp_u",
            email="transp.u@gmail.com",
            roles="transporteur",
        )
        self.user_transp.set_password("Admin1234!")
        self.user_transp.save()

        self.transporteur = Entreprise.objects.create(
            gerant=self.user_transp,
            raison_sociale="Transporteur SA",
            matricule_fiscal="1234567BAM333",
            type_entreprise="transporteur",
            adresse="Route de Zaghouan, 1005 Tunis, Tunisie",
        )

        self.vehicule = Vehicule.objects.create(
            immatriculation="190 TUN 9999",
            type_vehicule="camionnette",
            capacite_kg=1000,
            disponibilite=True,
            entreprise=self.transporteur,
        )

        self.expedition = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart="Tunis",
            ville_arrive="Sousse",
            date_souhaitée=timezone.now() + timedelta(days=3),
            poid_kg=Decimal("400.00"),
            statut="publiee",
            description="Lot de test",
        )

        self.admin_user = Utilisateur(
            username="admin_offre_test",
            email="admin.offre@gmail.com",
            roles=" admin",
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.set_password("Admin1234!")
        self.admin_user.save()

        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_dynamic_readonly_fields(self):
        site = AdminSite()
        admin_obj = OffreAdmin(Offre, site)
        rf = RequestFactory()
        req = rf.get("/admin/")

        offre = Offre.objects.create(
            expedition=self.expedition,
            transporteur=self.transporteur,
            vehicule=self.vehicule,
            prix=Decimal("300.00"),
            delai_jours=2,
            statut="proposee",
        )
        ro_initial = admin_obj.get_readonly_fields(req, offre)
        self.assertNotIn("prix", ro_initial)

        offre.statut = "acceptee"
        offre.save()

        ro_after = admin_obj.get_readonly_fields(req, offre)
        self.assertIn("prix", ro_after)
        self.assertIn("delai_jours", ro_after)

    def test_csv_export_action(self):
        offre = Offre.objects.create(
            expedition=self.expedition,
            transporteur=self.transporteur,
            vehicule=self.vehicule,
            prix=Decimal("250.00"),
            delai_jours=3,
            statut="proposee",
        )

        url = reverse("admin:OffreApp_offre_changelist")
        res = self.client.post(
            url,
            {
                "action": "exporter_offres_csv",
                "_selected_action": [offre.id],
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "text/csv")
        content = res.content.decode("utf-8")
        self.assertIn("reference_expedition,transporteur,prix,statut", content)
        self.assertIn("250.00", content)

    def test_health_check_endpoint(self):
        url = reverse("admin:health_check")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Tableau de bord de contrôle d'intégrité")
