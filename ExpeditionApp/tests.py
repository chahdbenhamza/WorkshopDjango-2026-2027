from datetime import timedelta
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from EntrepriseApp.models import Utilisateur, Entreprise
from ExpeditionApp.admin import ExpeditionAdmin, EnRetardFilter
from ExpeditionApp.models import Expedition


class ExpeditionAdminTests(TestCase):
    def setUp(self):
        self.user_chargeur = Utilisateur(
            username="chargeur_test",
            email="chargeur.test@gmail.com",
            roles="chargeur",
        )
        self.user_chargeur.set_password("Admin1234!")
        self.user_chargeur.save()

        self.chargeur = Entreprise.objects.create(
            gerant=self.user_chargeur,
            raison_sociale="Chargeur Test SA",
            matricule_fiscal="1234567AAM111",
            type_entreprise="chargeur",
            adresse="Avenue Habib Bourguiba, 1000 Tunis, Tunisie",
        )

        self.admin_user = Utilisateur(
            username="admin_test",
            email="admin.test@gmail.com",
            roles=" admin",
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.set_password("Admin1234!")
        self.admin_user.save()

        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_cloturer_expeditions_action(self):
        exp_en_cours = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart="Tunis",
            ville_arrive="Sfax",
            date_souhaitée=timezone.now() + timedelta(days=2),
            poid_kg=Decimal("300.00"),
            statut="en_cours",
            description="Colis urgent",
        )
        exp_autre = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart="Tunis",
            ville_arrive="Gabes",
            date_souhaitée=timezone.now() + timedelta(days=2),
            poid_kg=Decimal("300.00"),
            statut="publiee",
            description="Colis standard",
        )

        url = reverse("admin:ExpeditionApp_expedition_changelist")
        res = self.client.post(
            url,
            {
                "action": "cloturer_expeditions",
                "_selected_action": [exp_en_cours.id, exp_autre.id],
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)

        exp_en_cours.refresh_from_db()
        exp_autre.refresh_from_db()

        self.assertEqual(exp_en_cours.statut, "livrée")
        self.assertEqual(exp_autre.statut, "publiee")

    def test_en_retard_filter(self):
        exp_retard = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart="Tunis",
            ville_arrive="Nabeul",
            date_souhaitée=timezone.now() - timedelta(days=2),
            poid_kg=Decimal("200.00"),
            statut="publiee",
            description="En retard",
        )
        exp_futur = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart="Tunis",
            ville_arrive="Bizerte",
            date_souhaitée=timezone.now() + timedelta(days=2),
            poid_kg=Decimal("200.00"),
            statut="publiee",
            description="Dans les temps",
        )

        site = AdminSite()
        admin_obj = ExpeditionAdmin(Expedition, site)

        f_oui = EnRetardFilter(None, {"en_retard": ["oui"]}, Expedition, admin_obj)
        qs_oui = f_oui.queryset(None, Expedition.objects.all())
        self.assertIn(exp_retard, qs_oui)
        self.assertNotIn(exp_futur, qs_oui)

        f_non = EnRetardFilter(None, {"en_retard": ["non"]}, Expedition, admin_obj)
        qs_non = f_non.queryset(None, Expedition.objects.all())
        self.assertNotIn(exp_retard, qs_non)
        self.assertIn(exp_futur, qs_non)



class ExpeditionCRUDViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Utilisateur(
            username="chargeur_crud_user",
            email="chargeur.crud@gmail.com",
            roles="chargeur",
        )
        self.user.set_password("Password123!")
        self.user.save()
        self.entreprise = Entreprise.objects.create(
            gerant=self.user,
            raison_sociale="Chargeur Crud Express",
            matricule_fiscal="1234567AAM777",
            type_entreprise="chargeur",
            adresse="Avenue Habib Bourguiba, 1000 Tunis, Tunisie",
        )
        self.expedition = Expedition.objects.create(
            entreprise=self.entreprise,
            ville_depart="Tunis",
            ville_arrive="Sousse",
            date_souhaitée=timezone.now() + timedelta(days=3),
            poid_kg=Decimal("500.00"),
            statut="publiee",
            description="Lot de pièces détachées",
        )
        self.client.force_login(self.user)

    def test_list_expeditions(self):
        res = self.client.get(reverse('expeditions:liste_expeditions'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.expedition.reference)

    def test_detail_expedition(self):
        res = self.client.get(reverse('expeditions:detail', args=[self.expedition.reference]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.expedition.reference)

    def test_create_expedition(self):
        date_str = (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
        res = self.client.post(
            reverse('expeditions:create'),
            {
                'ville_depart': 'Bizerte',
                'ville_arrive': 'Sfax',
                'date_souhaitée': date_str,
                'poid_kg': '750.00',
                'statut': 'publiee',
                'entreprise': self.entreprise.pk,
                'description': 'Nouvelle expédition test',
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Expedition.objects.filter(ville_depart='Bizerte').exists())

    def test_delete_expedition(self):
        res = self.client.post(
            reverse('expeditions:delete', args=[self.expedition.pk]),
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Expedition.objects.filter(pk=self.expedition.pk).exists())

    def test_expedition_pages_require_login(self):
        anonymous_client = Client()
        protected_urls = [
            reverse('expeditions:liste_expeditions'),
            reverse('expeditions:detail', args=[self.expedition.reference]),
            reverse('expeditions:create'),
            reverse('expeditions:update', args=[self.expedition.pk]),
            reverse('expeditions:delete', args=[self.expedition.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = anonymous_client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse('login')))
