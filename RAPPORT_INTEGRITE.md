# Rapport de Contrôle d'Intégrité Métier — TransConnect
**Auteur :** Chahd Ben Hamza (Projet TransConnect)  
**Module :** Python Framework for the Web (Django) — 2026-2027  
**Livrable :** Section VIII & X — Travail individuel & Tableau de bord d'intégrité  

---

## 1. Contexte & Architecture du Tableau de Bord

Lors de la manipulation guidée (Section VII de l'énoncé), il a été démontré que des opérations SQL directes en masse via `.update()` ou `.bulk_update()` contournent totalement les méthodes `clean()`, `full_clean()` et `save()` des modèles Django. Cela provoque des corruptions silencieuses de données et des violations des règles métier sans lever d'exception en base.

Pour prévenir et détecter ces incohérences en production, nous avons développé un **Tableau de Bord de Contrôle d'Intégrité Métier**, accessible dans l'espace d'administration Django via l'URL dédiée :
```
/admin/health-check/
```

### Intégration technique :
1. **Surcharge de `get_urls()` sur le site admin** : Enregistrement de la route personnalisée via `admin.site.get_urls` dans `EntrepriseApp/admin.py`, protégée par `admin.site.admin_view`.
2. **Requêtes 100% ORM optimisées** : Aucune boucle Python de filtrage. Toutes les vérifications exploitent les capacités analytiques du moteur ORM Django (`filter`, `exclude`, `annotate`, `Count`, `distinct`).
3. **Template d'administration personnalisé (`templates/admin/health_check.html`)** : Étend `admin/base_site.html` avec navigation, indicateurs de santé (KPIs) en temps réel, alertes visuelles et liens directs vers la consultation/modification des fiches admin Django pour chaque objet en anomalie.

---

## 2. Analyse détaillée des Contrôles d'Intégrité Implémentés

Le tableau de bord surveille **6 contrôles d'intégrité** (dont les 5 proposés dans l'énoncé et un contrôle ciblant spécifiquement le piège de la cascade d'acceptation) :

### Contrôle 1 : Offres orphelines
* **Description :** Offres au statut `proposee` ou `acceptee` dont l'expédition associée n'est plus ni `publiee` ni `attribue(e)` (par exemple expédition annulée ou livrée).
* **Requête ORM :**
  ```python
  offres_orphelines = (
      Offre.objects
      .filter(statut__in=['proposee', 'acceptee'])
      .exclude(expedition__statut__in=['publiee', 'Publiée', 'publiée', 'attribue', 'Attribue', 'attribuee'])
      .select_related('expedition', 'transporteur', 'vehicule')
  )
  ```
* **(a) Règle métier protégée :** Règle métier relative au cycle de vie synchronisé des offres et expéditions. Une offre active ne peut exister que sur une expédition en phase de négociation (`publiee`) ou d'attribution (`attribuee`).
* **(b) Scénario réaliste en production :** Un administrateur ou un script cron de nettoyage exécute un `Expedition.objects.filter(statut='en_cours').update(statut='annulée')` sans passer par les modèles. Les offres déposées restent `proposee` ou `acceptee` alors que le fret n'existe plus.

---

### Contrôle 2 : Expéditions bloquées (> 7 jours)
* **Description :** Expéditions créées depuis plus de 7 jours consécutifs qui stagnent au statut `publiee` sans avoir trouvé de transporteur.
* **Requête ORM :**
  ```python
  seuil_7j = timezone.now() - timedelta(days=7)
  expeditions_bloquees = (
      Expedition.objects
      .filter(statut__in=['publiee', 'Publiée', 'publiée'], created_at__lt=seuil_7j)
      .select_related('entreprise')
  )
  ```
* **(a) Règle métier protégée :** Règle de fluidité du fret et de suivi opérationnel. Permet à l'équipe exploitation d'identifier les goulets d'étranglement ou les demandes sous-tarifiées.
* **(b) Scénario réaliste en production :** Une expédition publiée par un chargeur sur une destination peu desservie ou avec un tarif peu attractif n'a reçu aucune offre. Le chargeur l'a oubliée sans l'annuler.

---

### Contrôle 3 : Transporteurs sans flotte
* **Description :** Comptes entreprises enregistrés sous le type `transporteur` ne possédant aucun véhicule enregistré dans leur parc.
* **Requête ORM (conforme à l'exemple de l'énoncé) :**
  ```python
  from django.db.models import Count
  transporteurs_sans_flotte = (
      Entreprise.objects
      .filter(type_entreprise='transporteur')
      .annotate(nb_vehicules=Count('vehicules'))
      .filter(nb_vehicules=0)
      .select_related('gerant')
  )
  ```
* **(a) Règle métier protégée :** Règle d'éligibilité des transporteurs. Une entreprise ne peut se qualifier de transporteur et émettre des offres sans capacité matérielle vérifiable.
* **(b) Scénario réaliste en production :** Inscription en masse de transporteurs via une API partenaire (ex. onboarding B2B) où les comptes entreprises sont insérés avant les véhicules, ou suppression brute de véhicules via `Vehicule.objects.filter(...).delete()`.

---

### Contrôle 4 : Incohérence de disponibilité des véhicules
* **Description :** Véhicules marqués `disponibilite=True` alors qu'ils sont actuellement engagés dans une offre au statut `acceptee`.
* **Requête ORM :**
  ```python
  vehicules_incoherents = (
      Vehicule.objects
      .filter(disponibilite=True, offre__statut='acceptee')
      .distinct()
      .select_related('entreprise')
  )
  ```
* **(a) Règle métier protégée :** Règle d'exclusivité d'engagement. Un véhicule ne peut être affecté simultanément à plusieurs expéditions.
* **(b) Scénario réaliste en production :** Une action admin ou un script d'attribution passe des offres à `acceptee` par `.update(statut='acceptee')` sans déclencher la mise à jour correspondante `vehicule.disponibilite = False`.

---

### Contrôle 5 : Doublons de proposition d'offres
* **Description :** Un même transporteur possédant plusieurs offres simultanément au statut `proposee` sur une même expédition.
* **Requête ORM :**
  ```python
  groupes_doublons = (
      Offre.objects
      .filter(statut='proposee')
      .values('expedition_id', 'transporteur_id')
      .annotate(total=Count('id'))
      .filter(total__gt=1)
  )
  ```
* **(a) Règle métier protégée :** Règle métier n°4 du workshop Models (une entreprise transporteur ne peut maintenir qu'une seule proposition active par expédition).
* **(b) Scénario réaliste en production :** Problème de double soumission HTTP (retry automatique suite à un timeout réseau sans clé d'idempotence), ou script d'import en masse d'offres sans validation d'unicité.

---

### Contrôle 6 (Spécifique Démo Section VII) : Désynchronisation de cascade d'acceptation
* **Description :** Expédition restée au statut `publiee` alors qu'au moins une offre rattachée est passée au statut `acceptee`.
* **Requête ORM :**
  ```python
  expeditions_non_attribuees = (
      Expedition.objects
      .filter(statut__in=['publiee', 'Publiée', 'publiée'], offre__statut='acceptee')
      .distinct()
      .select_related('entreprise')
  )
  ```
* **(a) Règle métier protégée :** Règle métier n°5 du workshop Models (l'acceptation d'une offre doit immédiatement basculer l'expédition au statut `attribuee` et rejeter les offres concurrentes).
* **(b) Scénario réaliste en production :** C'est exactement l'anomalie provoquée sur `EXP-26-00001` par `Offre.objects.filter(pk=4).update(statut='acceptee')` lors de l'étape 6 de la section VII.

---

## 3. Résultats obtenus sur les données du projet

L'exécution du tableau de bord sur notre base de données locale (`chahd.sqlite3`) produit le résultat suivant :

```text
=== TABLEAU DE BORD D'INTÉGRITÉ TRANSCONNECT (/admin/health-check/) ===
Total contrôles exécutés : 6
Contrôles conformes      : 3 (50%)
Contrôles en alerte      : 3 (50%)
Total anomalies détectées: 4

[CONFORME] 1. Offres orphelines                                  : 0 anomalie
[ALERTE]   2. Expéditions bloquées (> 7 jours)                   : 1 anomalie (EXP-26-00001 créée le 14/10/2026)
[CONFORME] 3. Transporteurs sans flotte                          : 0 anomalie
[ALERTE]   4. Incohérence de disponibilité des véhicules         : 2 anomalies (215 TUN 9845, 199 TUN 1111)
[CONFORME] 5. Doublons de propositions d'offres                  : 0 anomalie
[ALERTE]   6. Expéditions non attribuées malgré offre acceptée   : 1 anomalie (EXP-26-00001)
```

### Justification des anomalies détectées :
1. **EXP-26-00001 (Expédition bloquée & Cascade rompue) :**
   Conformément à la consigne de l'étape 9 de la section VII (*« Ne pas nettoyer les données : Conservez EXP-26-00001 telle quelle après la démo »*), cette expédition a subi la mise à jour directe en SQL via `.update(statut='acceptee')` sur son offre. Elle met en évidence les contrôles n°2 et n°6 : l'expédition est restée en `publiee` depuis plus de 7 jours malgré une offre acceptée.
2. **Véhicules 215 TUN 9845 et 199 TUN 1111 (Disponibilité incohérente) :**
   Ces véhicules sont affectés à des offres acceptées sans que leur flag `disponibilite` n'ait été positionné à `False` en base, illustrant parfaitement l'effet pervers d'une mise à jour sans cascade métier complète.

---

## 4. Analyse critique de l'usage des Assistants IA

### Question imposée :
> *« Si vous avez utilisé un assistant IA pour cette partie : précisez dans votre rapport si l'outil a spontanément proposé une requête basée sur `.update()` / `.bulk_create()` plutôt que sur `annotate`/`aggregate`, et ce que cela vous apprend sur les limites de ces outils pour ce type de tâche. »*

### Réflexion & Constats :
1. **Biais de performance des modèles de langage :**
   Lorsqu'on demande naïvement à un modèle LLM d'optimiser une mise à jour ou de vérifier des volumes de données en Django, son réflexe statistique dominant est de privilégier la rapidité brute d'exécution en SQL. Il propose presque systématiquement des méthodes comme `.update()`, `.bulk_create()` ou des listes en compréhension avec boucles Python.
2. **Ignorance du modèle d'événements et de validation Django :**
   Un assistant IA non guidé ignore que `.update()` court-circuite `full_clean()`, `clean()` et `save()`. Il ne prend pas conscience que la cohérence transactionnelle et les cascades applicatives de TransConnect (règle métier n°5) reposent sur ces méthodes Python.
3. **Apprentissage et bonnes pratiques :**
   Pour les requêtes d'analyse et de contrôle d'intégrité, les primitives `annotate()` et `aggregate()` doivent être explicitement exigées. Cela montre que l'intelligence artificielle est un accélérateur d'écriture puissant, mais qu'elle ne remplace en aucun cas la rigueur de modélisation du développeur, qui doit conserver la maîtrise des garanties d'intégrité et de validation du framework.

