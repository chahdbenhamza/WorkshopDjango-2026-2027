## Entrée 2026-10-2
- Outil IA utilisé : Claude (Anthropic)
- Prompt : « Analyser le snippet code du modèle Offre fourni dans le workshop TransConnect. Identifie les 4 anomalies par rapport au cahier des charges communiqué et proposer les solutions avec les justifications. » (cahier des charges et snippet joints)
- Sortie obtenue (résumé) : Claude a repéré 4 anomalies dans le modèle, signalé un point en plus (le `null=True` sur `vehicule`) et proposé une version corrigée de `Offre`, avec `STATUT_CHOICES`, `created_at` / `updated_at` et un `save()` qui gère l'acceptation d'une offre.
- Écarts identifiés vs cahier des charges :
  1. `prix` est en `CharField(max_length=10)`, alors que le sujet demande un `DecimalField`.
  2. `delai_jours` est en `IntegerField`, alors que le sujet demande un `PositiveIntegerField`.
  3. `date_proposition` utilise `auto_now=True`, alors qu'il faut `auto_now_add=True`.
  4. Le `save()` ne fait qu'appeler `super().save()`, donc accepter une offre ne déclenche rien, alors que le sujet parle d'effets en cascade.
  5. En plus : `vehicule` a `null=True`, alors qu'une offre doit être liée à un véhicule du transporteur. Il manque aussi `STATUT_CHOICES`, `created_at` et `updated_at`.
- Correction apportée et justification :
  1. `DecimalField(max_digits=10, decimal_places=2)`. Avec un `CharField`, on ne peut pas trier ni faire de sommes ou de comparaisons sur les prix, et n'importe quelle chaîne est acceptée.
  2. `PositiveIntegerField()`. Un délai en jours ne peut pas être négatif, et Django ajoute une contrainte en base.
  3. `auto_now_add=True`. Avec `auto_now`, la date serait écrasée à chaque sauvegarde, par exemple quand l'offre passe à `acceptee`, alors qu'on veut la date de la proposition.
  4. Logique ajoutée dans `save()` avec `transaction.atomic()` : si le statut est `acceptee`, l'expédition passe à `attribuee` et les autres offres `proposee` de cette expédition passent à `refusee`. Les effets en cascade ne sont pas détaillés dans la Part 1 du sujet, donc c'est une hypothèse à vérifier.
  5. Suppression de `null=True`, définition de `STATUT_CHOICES` et ajout de `created_at` et `updated_at`, comme le sujet l'impose pour tous les modèles.


## Entrée 2026-10-27
- Outil IA utilisé : Antigravity / Gemini 3.8 Flash
- Prompt : « ANALYSE LES FICHIER PROPERLY ET TERMINER LES PARTIES MANQUANTES DU LENONCE EN RESPECTANT LE CODE DE L'ENSEIGNANT » (Workshop Python Framework Partie Admin — TransConnect)
- Sortie obtenue (résumé) :
  1. Audit complet des 4 applications (`EntrepriseApp`, `VehiculesApp`, `ExpeditionApp`, `OffreApp`) et comparaison avec les 8 pages du sujet.
  2. Complétion de `admin.py` dans chaque application :
     - Ajout de `OffreInline` (`StackedInline` avec `show_change_link=True` et `can_delete=False`) sur `ExpeditionAdmin`.
     - Finalisation de `VehiculeInline` (`TabularInline`, `extra=0`, champs définis) sur `EntrepriseAdmin`.
     - Ajout de la colonne calculée avec badge coloré de statut (`statut_colore`) pour `Expedition` et harmonisation sur `Offre`.
     - Ajout de l'édition rapide `list_editable = ('disponibilite',)` sur `VehiculeAdmin`.
     - Ajout de l'action personnalisée `exporter_offres_csv` avec `HttpResponse` et `select_related` sur `OffreAdmin`.
     - Renommage et renforcement de l'action `cloturer_expeditions` avec `full_clean()` et `save()`.
     - Implémentation de la lecture seule dynamique via `get_readonly_fields` sur `OffreAdmin` (verrouillage de `prix` et `delai_jours` après acceptation).
     - Configuration du branding TransConnect (`site_header`, `site_title`, `index_title`).
  3. Création de la commande de gestion `EntrepriseApp/management/commands/seed_demo.py` pour générer le jeu de données démo (`EXP-26-00001` et `EXP-26-00002`) et test de la manipulation à risque de la Section VII.
  4. Réalisation du Tableau de Bord de Contrôle d'Intégrité (Section VIII) accessible via `/admin/health-check/` avec surcharge de `get_urls()` sur le site admin, 6 contrôles ORM (sans boucle Python), template personnalisé et rédaction du rapport complet `RAPPORT_INTEGRITE.md`.
- Écarts et pièges identifiés vs ORM en masse :
  - L'assistant a été interrogé sur la mise en œuvre de requêtes en masse et a spontanément pu privilégier `.update()`. L'obligation d'utiliser `annotate()` / `Count()` et d'éviter les contournements de `save()` a été rigoureusement respectée pour garantir la cohérence des règles métier du workshop Models.
