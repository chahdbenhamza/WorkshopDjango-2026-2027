from django.test import TestCase, Client
from django.urls import reverse
from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule


class VehiculeCRUDViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Utilisateur(
            username="transp_test_user",
            email="transp.test@gmail.com",
            roles="transporteur",
        )
        self.user.set_password("Password123!")
        self.user.save()

        self.entreprise = Entreprise.objects.create(
            gerant=self.user,
            raison_sociale="Transporteur Test Flotte",
            matricule_fiscal="1234567AAM888",
            type_entreprise="transporteur",
            adresse="Avenue Habib Bourguiba, 1000 Tunis, Tunisie",
        )
        self.vehicule = Vehicule.objects.create(
            immatriculation="180 TUN 4321",
            type_vehicule="camionnette",
            capacite_kg=1200,
            disponibilite=True,
            entreprise=self.entreprise,
        )

    def test_list_vehicules(self):
        res = self.client.get(reverse('vehicules:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "180 TUN 4321")

    def test_create_vehicule(self):
        res = self.client.post(
            reverse('vehicules:create'),
            {
                'immatriculation': '190 TUN 5555',
                'type_vehicule': 'fourgon',
                'capacite_kg': 2500,
                'entreprise': self.entreprise.pk,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Vehicule.objects.filter(immatriculation='190 TUN 5555').exists())

    def test_update_vehicule(self):
        res = self.client.post(
            reverse('vehicules:update', args=[self.vehicule.pk]),
            {
                'immatriculation': '180 TUN 4321',
                'type_vehicule': 'fourgon',
                'capacite_kg': 3000,
                'entreprise': self.entreprise.pk,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.vehicule.refresh_from_db()
        self.assertEqual(self.vehicule.capacite_kg, 3000)

    def test_delete_vehicule(self):
        res = self.client.post(
            reverse('vehicules:delete', args=[self.vehicule.pk]),
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Vehicule.objects.filter(pk=self.vehicule.pk).exists())
