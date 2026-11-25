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
        self.client.force_login(self.user)
        res = self.client.get(reverse('entreprises:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Maghreb Fret Test")

    def test_create_entreprise(self):
        self.client.force_login(self.user2)
        res = self.client.post(
            reverse('entreprises:create'),
            {
                'raison_sociale': 'Nouvelle Entreprise SA',
                'matricule_fiscal': '1234567BAM555',
                'type_entreprise': 'chargeur',
                'adresse': 'Zone Industrielle Megrine, 2033 Megrine, Tunisie',
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        entreprise = Entreprise.objects.get(matricule_fiscal='1234567BAM555')
        self.assertEqual(entreprise.gerant, self.user2)

    def test_create_entreprise_requires_login_and_hides_manager_field(self):
        response = self.client.get(reverse('entreprises:create'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

        self.client.force_login(self.user)
        response = self.client.get(reverse('entreprises:create'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="gerant"')

    def test_update_entreprise(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse('entreprises:update', args=[self.entreprise.pk]),
            {
                'raison_sociale': 'Maghreb Fret Modifie',
                'matricule_fiscal': '1234567AAM666',
                'type_entreprise': 'transporteur',
                'adresse': 'Avenue Habib Bourguiba, 1000 Tunis, Tunisie',
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.entreprise.refresh_from_db()
        self.assertEqual(self.entreprise.raison_sociale, 'Maghreb Fret Modifie')
        self.assertEqual(self.entreprise.gerant, self.user)

    def test_delete_entreprise(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse('entreprises:delete', args=[self.entreprise.pk]),
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Entreprise.objects.filter(pk=self.entreprise.pk).exists())

    def test_enterprise_pages_require_login(self):
        protected_urls = [
            reverse('entreprises:list'),
            reverse('entreprises:detail', args=[self.entreprise.pk]),
            reverse('entreprises:update', args=[self.entreprise.pk]),
            reverse('entreprises:delete', args=[self.entreprise.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse('login')))


class InscriptionViewTests(TestCase):
    def test_displays_signup_fields(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        for field in ('username', 'email', 'telephone', 'password1', 'password2'):
            self.assertContains(response, f'name="{field}"')

    def test_registers_user_with_phone_and_password(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'nouvel_utilisateur',
                'email': 'nouvel.utilisateur@gmail.com',
                'telephone': '0612345678',
                'password1': 'SafePassword123!',
                'password2': 'SafePassword123!',
            },
        )

        self.assertRedirects(response, reverse('entreprises:create'))
        user = Utilisateur.objects.get(username='nouvel_utilisateur')
        self.assertEqual(user.telephone, '0612345678')
        self.assertTrue(user.check_password('SafePassword123!'))
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'nouvel_utilisateur',
                'email': 'nouvel.utilisateur@gmail.com',
                'telephone': '0612345678',
                'password1': 'SafePassword123!',
                'password2': 'DifferentPassword123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Utilisateur.objects.filter(username='nouvel_utilisateur').exists()
        )
