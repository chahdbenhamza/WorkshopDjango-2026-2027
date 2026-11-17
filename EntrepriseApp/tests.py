from django.test import TestCase, Client
from django.urls import reverse
from EntrepriseApp.models import Utilisateur, Entreprise


class EntrepriseCRUDViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Utilisateur(
            username="gerant_test",
            email="gerant.test@gmail.com",
            roles="chargeur",
        )
        self.user.set_password("Password123!")
        self.user.save()

        self.user2 = Utilisateur(
            username="gerant_test2",
            email="gerant.test2@gmail.com",
            roles="transporteur",
        )
        self.user2.set_password("Password123!")
        self.user2.save()

        self.entreprise = Entreprise.objects.create(
            gerant=self.user,
            raison_sociale="Maghreb Fret Test",
            matricule_fiscal="1234567AAM666",
            type_entreprise="transporteur",
            adresse="Avenue Habib Bourguiba, 1000 Tunis, Tunisie",
        )

    def test_list_entreprises(self):
        res = self.client.get(reverse('entreprises:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Maghreb Fret Test")

    def test_create_entreprise(self):
        res = self.client.post(
            reverse('entreprises:create'),
            {
                'raison_sociale': 'Nouvelle Entreprise SA',
                'matricule_fiscal': '1234567BAM555',
                'type_entreprise': 'chargeur',
                'adresse': 'Zone Industrielle Megrine, 2033 Megrine, Tunisie',
                'gerant': self.user2.pk,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Entreprise.objects.filter(matricule_fiscal='1234567BAM555').exists())

    def test_update_entreprise(self):
        res = self.client.post(
            reverse('entreprises:update', args=[self.entreprise.pk]),
            {
                'raison_sociale': 'Maghreb Fret Modifie',
                'matricule_fiscal': '1234567AAM666',
                'type_entreprise': 'transporteur',
                'adresse': 'Avenue Habib Bourguiba, 1000 Tunis, Tunisie',
                'gerant': self.user.pk,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.entreprise.refresh_from_db()
        self.assertEqual(self.entreprise.raison_sociale, 'Maghreb Fret Modifie')

    def test_delete_entreprise(self):
        res = self.client.post(
            reverse('entreprises:delete', args=[self.entreprise.pk]),
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Entreprise.objects.filter(pk=self.entreprise.pk).exists())
