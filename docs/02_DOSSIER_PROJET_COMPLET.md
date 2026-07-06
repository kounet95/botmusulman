# Dossier de projet complet
# MosquéeBot Guinée — Implémentation à Conakry sous l'égide du Phoenix Club

**Version :** 1.0
**Date :** Juillet 2026
**Porteur du projet :** Phoenix Club
**Opérateur technique :** Alpha Oumar Diallo — Solutions numériques islamiques
**Contact :** kounetdiallo95@gmail.com / @alphaoumardiallo

> Ce document est une base de soumission. Les montants budgétaires sont des estimations indicatives à valider avec le Phoenix Club et les mosquées pilotes avant tout engagement financier.

---

## Sommaire

1. Contexte et problématique
2. Le porteur de projet : le Phoenix Club
3. Présentation de la solution MosquéeBot
4. Le module Guinée : programme de statuts communautaires
5. Bénéficiaires et zone cible
6. Gouvernance du projet
7. Plan de déploiement par phases
8. Budget prévisionnel
9. Feuille de route / calendrier
10. Impact attendu et indicateurs de suivi
11. Risques et mesures d'atténuation
12. Annexe technique

---

## 1. Contexte et problématique

À Conakry comme dans le reste de la Guinée, la vie des mosquées repose largement sur des circuits d'information informels : annonces orales après la prière, affichage papier, groupes WhatsApp non structurés. Cela entraîne plusieurs difficultés récurrentes :

- Les fidèles manquent des cours, conférences et halaqas faute d'information centralisée et de rappels.
- Les collectes de dons (rénovation, bourses, aide sociale) se font majoritairement en espèces, sans traçabilité ni visibilité sur l'objectif atteint — ce qui freine la générosité de la diaspora en particulier.
- Les mosquées n'ont pas de vision chiffrée de leur propre activité (nombre de fidèles inscrits, taux de participation, montants collectés).
- L'engagement bénévole des fidèles (organisation d'événements, collecte de dons) n'est ni structuré ni valorisé.

Dans le même temps, la Guinée connaît une forte adoption du mobile (Orange Money, MTN Mobile Money) et une population jeune, connectée, en particulier via des applications de messagerie comme Telegram et WhatsApp.

**Le besoin identifié :** un outil numérique simple, gratuit pour le fidèle, qui centralise l'information religieuse et communautaire, fiabilise la collecte de dons, et valorise l'engagement bénévole — sans nécessiter de compétence technique de la part des responsables de mosquée.

## 2. Le porteur de projet : le Phoenix Club

Le Phoenix Club est à la fois l'initiateur officiel et le financeur du projet pour son implémentation en Guinée. À ce titre, il :

- porte la légitimité institutionnelle du projet auprès des mosquées et des autorités religieuses locales ;
- finance le don initial permettant l'adaptation, le développement et le déploiement du système ;
- supervise, via un comité de pilotage, le bon déroulement du projet et l'atteinte des objectifs fixés avec les mosquées bénéficiaires.

*[Section à compléter par le Phoenix Club : présentation officielle du club, ses statuts, ses réalisations antérieures, ses membres fondateurs.]*

## 3. Présentation de la solution MosquéeBot

MosquéeBot est une plateforme déjà conçue et fonctionnelle en version pilote, composée de trois composants techniques et d'une base de données commune.

### 3.1 Le bot Telegram (côté fidèle)

Accessible gratuitement via un simple lien Telegram propre à chaque mosquée, il propose :

| Fonction | Description |
|---|---|
| Horaires de prière | Horaires quotidiens calculés automatiquement selon la ville, avec la prochaine prière à venir |
| Activités | Liste des cours, conférences, halaqas et événements à venir, avec inscription directe et gestion de liste d'attente en cas de capacité atteinte |
| Mes cours | Suivi personnel des inscriptions du fidèle |
| Dons & Sadaqa | Liste des collectes actives avec barre de progression, don via Orange Money, MTN Mobile Money, ou lien de paiement en ligne |
| Notifications | Préférences personnalisables (horaires de prière, cours, conférences, annonces, Hajj/Omra) |
| Contenu religieux | Hadith, verset ou rappel envoyé automatiquement selon un calendrier programmé par la mosquée |
| Annonces | Diffusion des communiqués officiels de la mosquée à tous les fidèles inscrits |

### 3.2 Le tableau de bord d'administration (côté mosquée)

Interface web destinée à l'imam ou au bureau de la mosquée, avec authentification propre à chaque mosquée :

- Statistiques : nombre de fidèles inscrits, activités du mois, inscriptions totales, montant total des dons collectés.
- Gestion des activités : création, modification, suivi des inscriptions et de la capacité.
- Gestion des collectes de dons : création de campagnes, suivi de la progression, numéros Orange Money/MTN MoMo associés.
- Diffusion d'annonces et de contenu religieux programmé.

### 3.3 Architecture multi-mosquées

Une même infrastructure technique peut héberger un nombre illimité de mosquées, chacune avec :
- son propre lien d'accès Telegram (slug dédié) ;
- ses propres administrateurs et identifiants ;
- ses propres données (fidèles, activités, dons) isolées des autres mosquées.

**Conséquence pratique pour le projet :** le coût d'ajout d'une nouvelle mosquée après la phase pilote est marginal (pas de nouvelle infrastructure à créer), ce qui permet une extension progressive et peu coûteuse à d'autres quartiers de Conakry puis à l'intérieur du pays.

## 4. Le module Guinée : programme de statuts communautaires

C'est l'apport spécifique de cette implémentation, à développer avec le financement du Phoenix Club. Il n'existe pas dans la version actuelle du système.

### 4.1 Principe

Valoriser l'engagement des fidèles par un système de statuts progressifs, débloquant des fonctionnalités supplémentaires dans le bot et une reconnaissance au sein de la communauté.

### 4.2 Statuts proposés (base de discussion)

| Statut | Critère d'accès (proposé) | Fonctionnalités débloquées |
|---|---|---|
| **Fidèle** | Inscription simple au bot | Horaires, activités, dons, contenu religieux, annonces |
| **Contributeur** | Dons réguliers et/ou parrainage de nouveaux fidèles inscrits via un lien personnel | Badge visible, priorité d'inscription aux événements à capacité limitée |
| **Vendeur solidaire** | Validé par le bureau de la mosquée pour la collecte de dons ou la vente d'articles (produits halal, artisanat, ouvrages) au profit de la mosquée | Espace de suivi de ses propres collectes/ventes dans le bot, reçu automatique, classement de reconnaissance |
| **Stratège** | Coordination bénévole d'activités (cours, conférences, événements), validée par le bureau de la mosquée | Accès à des fonctions d'organisation dans le tableau de bord (création/suivi d'activités déléguées) |

### 4.3 Ce que cela implique techniquement

- Extension du schéma de base de données : table de statuts par fidèle, historique de parrainage, suivi des collectes attribuées à un « vendeur solidaire ».
- Nouvelles commandes et écrans dans le bot Telegram (mon statut, mes filleuls, mes collectes).
- Nouveaux écrans dans le tableau de bord pour que le bureau de la mosquée valide/attribue les statuts.
- Génération de liens de parrainage uniques par fidèle.

### 4.4 Points à trancher avec le Phoenix Club avant développement

- Les statuts sont-ils honorifiques uniquement, ou donnent-ils droit à une contrepartie matérielle (ex. pourcentage sur les ventes, prise en charge de frais de transport pour les bénévoles) ?
- Qui valide l'attribution d'un statut : l'imam, le bureau de la mosquée, ou le Phoenix Club ?
- Le programme est-il identique dans toutes les mosquées partenaires, ou adaptable mosquée par mosquée ?

## 5. Bénéficiaires et zone cible

- **Bénéficiaires directs :** les fidèles des mosquées partenaires (information, dons facilités, valorisation de l'engagement bénévole).
- **Bénéficiaires institutionnels :** les mosquées elles-mêmes (imams, bureaux), qui gagnent en visibilité sur leur activité et en capacité de collecte.
- **Zone cible phase 1 :** un nombre restreint de mosquées pilotes à Conakry, à sélectionner conjointement par le Phoenix Club et les autorités religieuses locales.
- **Zone cible phase 2+ :** extension progressive à d'autres mosquées de Conakry, puis à d'autres villes du pays.

## 6. Gouvernance du projet

| Rôle | Responsabilité |
|---|---|
| **Phoenix Club** | Portage institutionnel, financement, comité de pilotage, choix des mosquées bénéficiaires |
| **Opérateur technique** (Alpha Oumar Diallo) | Développement, adaptation locale, hébergement, maintenance, formation |
| **Bureau de chaque mosquée** | Utilisation quotidienne du tableau de bord, validation des statuts communautaires, relais auprès des fidèles |
| **Comité de pilotage** | Composé de représentants du Phoenix Club et des mosquées pilotes — suivi trimestriel de l'avancement et des indicateurs |

## 7. Plan de déploiement par phases

**Phase 0 — Cadrage (avant démarrage)**
Validation du présent dossier par le Phoenix Club, sélection de la ou des mosquées pilotes, désignation des interlocuteurs de chaque mosquée.

**Phase 1 — Adaptation et pilote (1 mosquée)**
Adaptation du système au contexte guinéen (villes, numéros Orange Money/MTN MoMo, langues), mise en place du bot et du tableau de bord pour la mosquée pilote, formation du bureau de la mosquée, lancement auprès des fidèles.

**Phase 2 — Programme de statuts communautaires**
Conception détaillée puis développement du module vendeur/stratège/contributeur, test sur la mosquée pilote.

**Phase 3 — Extension**
Déploiement sur un second groupe de mosquées à Conakry, intégration des retours d'expérience de la phase pilote.

**Phase 4 — Consolidation**
Bilan d'impact, ajustements, préparation d'une extension à d'autres villes si les résultats sont concluants.

## 8. Budget prévisionnel (indicatif)

*Montants à titre d'ordre de grandeur, en dollars américains (USD) — à convertir et ajuster en francs guinéens (GNF) selon les devis réels des prestataires locaux (hébergement, connectivité, formation).*

| Poste | Description | Estimation |
|---|---|---|
| Adaptation locale | Villes, langues, intégration Orange Money/MTN MoMo | À chiffrer |
| Développement du module statuts communautaires | Vendeur solidaire, stratège, contributeur, parrainage | À chiffrer |
| Hébergement & infrastructure | 12 mois, plusieurs mosquées sur une infrastructure mutualisée | À chiffrer |
| Formation | Sessions pour les bureaux de mosquée (utilisation du tableau de bord) | À chiffrer |
| Communication & lancement | Supports d'annonce en mosquée, affiches avec QR code d'accès au bot | À chiffrer |
| Maintenance & support (12 mois) | Support technique continu, corrections, petites évolutions | À chiffrer |
| Imprévus | Marge de sécurité (~10 %) | À chiffrer |

**Recommandation :** faire chiffrer précisément chaque poste avec l'opérateur technique avant la signature du don, sur la base du nombre de mosquées pilotes retenu par le Phoenix Club.

## 9. Feuille de route / calendrier indicatif

| Étape | Délai indicatif à partir du feu vert du Phoenix Club |
|---|---|
| Sélection de la mosquée pilote et cadrage | Semaine 1-2 |
| Adaptation technique locale | Semaine 3-6 |
| Formation du bureau de la mosquée pilote | Semaine 6-7 |
| Lancement auprès des fidèles | Semaine 8 |
| Développement du module statuts communautaires | Semaine 8-14 |
| Bilan de la phase pilote | Semaine 16 |
| Décision d'extension à d'autres mosquées | Semaine 17+ |

## 10. Impact attendu et indicateurs de suivi

| Objectif | Indicateur |
|---|---|
| Meilleure information des fidèles | Nombre de fidèles inscrits au bot par mosquée |
| Participation accrue aux activités | Taux de remplissage des cours/conférences, taux de présence effective |
| Dons facilités et transparents | Montant total collecté, nombre de dons par moyen de paiement |
| Engagement bénévole valorisé | Nombre de fidèles ayant atteint le statut « contributeur », « vendeur solidaire » ou « stratège » |
| Réplicabilité | Nombre de mosquées actives sur la plateforme, coût marginal par nouvelle mosquée |

## 11. Risques et mesures d'atténuation

| Risque | Mesure d'atténuation |
|---|---|
| Connectivité internet limitée dans certains quartiers | Fonctionnement du bot en léger consommation de données (Telegram est optimisé bas débit) ; prévoir un canal complémentaire (WhatsApp, affichage papier avec QR code) |
| Réticence à la digitalisation des dons | Conserver la possibilité du don en espèces en parallèle ; transparence totale sur les montants collectés pour construire la confiance |
| Faible appropriation par le bureau de la mosquée | Formation pratique obligatoire avant lancement, support technique de proximité |
| Ambiguïté sur les contreparties du statut « vendeur solidaire » | Trancher ce point avec le Phoenix Club avant développement (voir section 4.4) |
| Dépendance à un seul développeur | Documentation technique complète du système, code structuré et maintenable (voir annexe technique) |

## 12. Annexe technique

### 12.1 Architecture

- **Bot Telegram** : Python (python-telegram-bot).
- **API backend** : Python (FastAPI), authentification par mosquée.
- **Tableau de bord** : Angular.
- **Base de données** : PostgreSQL (Supabase), architecture multi-mosquées (une ligne `mosque_id` par mosquée sur chaque table).
- **Déploiement** : conteneurs Docker (bot, backend, dashboard, base de données), orchestrés via `docker-compose`.

### 12.2 Moyens de paiement déjà pris en charge par le schéma de données

- Orange Money (numéro dédié par campagne de don)
- MTN Mobile Money (numéro dédié par campagne de don)
- Lien de paiement en ligne générique (ex. Stripe, pour la diaspora)

### 12.3 Modules existants réutilisables tels quels

Horaires de prière, activités et inscriptions, liste d'attente, dons et collectes, contenu religieux programmé, annonces, statistiques du tableau de bord.

### 12.4 Modules à développer pour la Guinée

Programme de statuts communautaires (section 4), intégration approfondie Orange Money/MTN MoMo si un paiement direct dans le bot est souhaité (au-delà du simple numéro affiché), traduction/adaptation des contenus si nécessaire.

---

*Dossier préparé par Alpha Oumar Diallo — Solutions numériques islamiques*
*Contact : kounetdiallo95@gmail.com / @alphaoumardiallo*
