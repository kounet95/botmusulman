# Stratégie de financement élargie & modèle de rentabilité
## Complément au dossier Phoenix Club

**Version :** 1.0
**Date :** Juillet 2026
**À lire après :** `01_NOTE_DE_SYNTHESE.md` et `02_DOSSIER_PROJET_COMPLET.md`

> Ce document ne remplace pas le dossier Phoenix Club — il le complète. Le Phoenix Club reste le financeur de la **Phase 1 (pilote Conakry)**, financée par un don. Ce document répond à deux questions supplémentaires : comment financer les phases suivantes (au-delà du Phoenix Club), et comment le projet peut devenir rentable par lui-même une fois le pilote validé.

---

## Sommaire

1. Où en est le projet aujourd'hui (état réel, pas projeté)
2. Deux logiques de financement à mener en parallèle
3. Modèle économique : la commission sur les dons — ce qu'il faut construire avant
4. Cadrage éthique et religieux de la commission (point non négociable)
5. Projection illustrative (hypothèses, pas une promesse)
6. Autres revenus complémentaires (une fois la base installée)
7. Ce qui finance quoi, et quand
8. Prochaines étapes concrètes

---

## 1. Où en est le projet aujourd'hui

Pour être utile face à un bailleur ou un investisseur, ce document part de l'état réel du système, pas d'une version idéalisée :

- **1 mosquée réelle en production** (Conakry) + une mosquée pilote historique (Gatineau, Canada) qui a servi de démonstrateur technique.
- Le bot, le tableau de bord, l'écran d'affichage TV et le pipeline de déploiement (CI/CD) sont **construits et fonctionnels**, pas de simples maquettes.
- Les dons via Orange Money / MTN Mobile Money sont aujourd'hui **affichés** dans le bot (numéro + lien) — le fidèle effectue lui-même le transfert en dehors de la plateforme. **La plateforme ne touche pas encore l'argent.** C'est la limite technique centrale à lever avant toute commission (section 3).
- Aucune levée de fonds ni subvention n'est encore signée à ce jour ; le dossier Phoenix Club est la première démarche de financement engagée.

Cette honnêteté sur l'état d'avancement est un atout dans un dossier : elle montre que ce qui est promis est réaliste, pas survendu.

---

## 2. Deux logiques de financement à mener en parallèle

Vous avez choisi de ne pas trancher entre les deux — voici comment elles se complètent plutôt que de s'exclure.

### A. Subventions / bailleurs (financement non dilutif)

**Logique :** on vous donne de l'argent pour un impact social démontré, sans prise de participation. C'est la voie naturelle pour la Phase 1 (déjà engagée avec le Phoenix Club) et pour la réplication à d'autres villes.

Pistes à explorer et vérifier (éligibilité, montants, calendriers changent souvent — à confirmer directement auprès de chaque structure) :

| Piste | Pourquoi c'est pertinent ici |
|---|---|
| **Orange Digital Center Guinée** | Orange porte déjà un programme d'appui aux startups/projets numériques en Guinée ; le projet utilise Orange Money nativement — angle d'entrée naturel. |
| **MTN Foundation / programmes RSE MTN Guinée** | Même logique côté MTN Mobile Money ; les opérateurs télécoms financent volontiers des cas d'usage qui augmentent l'adoption de leur mobile money. |
| **Banque Islamique de Développement (BID) — fonds PME/innovation** | Le projet sert une cause religieuse et communautaire ; la BID finance des projets d'impact dans les pays membres, dont la Guinée. |
| **UNCDF (UN Capital Development Fund)** | Mandat spécifique sur l'inclusion financière numérique en Afrique de l'Ouest — la brique mobile money est directement dans leur cœur de cible. |
| **GIZ Guinée (coopération allemande)** | Actif sur les programmes d'économie numérique en Guinée. |
| **Concours civic tech / tech-for-good** (Seedstars Africa, MEST Africa, Google for Startups Africa) | Visibilité + financement/accompagnement, sans dilution ; bon complément à une subvention institutionnelle. |
| **Diaspora guinéenne** | Cible naturelle pour du don ou du financement participatif — c'est elle qui, selon le constat même du dossier Phoenix Club, hésite aujourd'hui à donner faute de traçabilité. Le produit répond exactement à leur frein. |

**Avantage pour ce projet précis :** dossier déjà à moitié écrit (docs 01/02), impact social facile à démontrer, aucune dilution.
**Limite :** cycles de décision souvent longs (plusieurs mois), montants parfois modestes, reporting d'impact exigé en continu.

### B. Investisseurs / accélérateurs (financement dilutif)

**Logique :** on investit dans une entreprise qui vise une croissance et un modèle de revenus clair, en échange de parts.

Pistes à explorer : Orange Fab (accélérateur du groupe Orange, présent dans plusieurs pays africains), MEST Africa, Founder Institute (chapitres Afrique), business angels spécialisés fintech/civic tech africain.

**Avantage :** capital plus important, accès à un réseau, décisions parfois plus rapides qu'un bailleur institutionnel.
**Limite, à dire clairement :** un investisseur voudra un **modèle de revenus qui fonctionne déjà un minimum** (traction, premiers paiements réels traités par la plateforme) avant d'investir. Aujourd'hui, avec 1 mosquée et aucune transaction réellement traitée par le système, ce projet **n'est pas encore prêt pour cette voie** — la section 3 explique ce qu'il faut construire pour l'être.

**Recommandation :** utiliser la subvention (Phoenix Club + éventuellement une deuxième) pour financer la Phase 1 *et* la construction du module de paiement intégré (section 3). C'est cette traction (mosquées actives + volume de dons réellement traité) qui rendra le dossier investisseur crédible ensuite — pas avant.

---

## 3. Modèle économique : la commission sur les dons

Vous avez choisi ce modèle en priorité. Il est cohérent avec le produit (le don est déjà au centre du bot), mais il faut être précis sur ce qu'il implique **techniquement** — ce n'est pas juste une case à cocher dans le tableau de bord.

### 3.1 Le prérequis technique : sortir du simple affichage de numéro

Aujourd'hui, un don Orange Money/MTN se fait **en dehors** du système (le fidèle compose lui-même le transfert). Pour prélever une commission, l'argent doit **transiter par la plateforme**, ce qui veut dire intégrer réellement :

- **Orange Money API** (Guinée) — paiement marchand/collecte.
- **MTN MoMo API (Collections)** — équivalent côté MTN.
- Un compte agrégateur/marchand pour la plateforme, avec les démarches réglementaires que cela implique (identification, conformité, potentiellement un agrément auprès de la BCRG selon les seuils traités — **à vérifier avec un conseil juridique local avant tout lancement**, ce n'est pas une formalité anodine).
- Une logique de reversement automatique : le don arrive sur le compte plateforme, la plateforme reverse *(montant du don − commission)* à la mosquée selon un cycle défini (ex. hebdomadaire).

C'est un chantier technique et réglementaire à part entière — sensiblement plus gros que ce qui existe aujourd'hui (affichage de numéro). Il doit être budgété comme tel dans un futur avenant au dossier Phoenix Club ou dans une subvention dédiée.

### 3.2 Ce que ça change pour le module "vendeur solidaire" déjà prévu

Le dossier Phoenix Club (section 4) prévoit déjà un statut "vendeur solidaire" avec suivi de collectes. Une fois le paiement intégré, ce module devient beaucoup plus riche : reçu automatique horodaté, traçabilité complète pour la mosquée *et* pour le donateur — exactement le frein de la diaspora que le dossier identifie en section 1.

---

## 4. Cadrage éthique et religieux — point non négociable

Prélever une commission sur la sadaqa (aumône) ou le don à une mosquée est un sujet sensible qui touche à des questions de fiqh. Ce projet ne peut pas trancher ça seul.

**Recommandation ferme :**
1. **Ne jamais prélever silencieusement sur le montant du don.** Le fidèle qui donne 100 000 GNF doit voir que 100 000 GNF sont crédités à la mosquée.
2. Modèle à privilégier : **frais de service transparents, ajoutés en plus du don, à la charge du donateur qui peut voir et accepter ce frais avant de valider** (comme le fait GoFundMe : "ajouter X pour couvrir les frais de la plateforme"). Le fidèle choisit ; la mosquée reçoit 100 % de son don.
3. **Faire valider ce mécanisme par des oulémas/imams locaux avant tout déploiement** — idéalement les mêmes autorités religieuses associées au choix de la mosquée pilote (dossier Phoenix Club, section 5). Une validation religieuse explicite est aussi un argument de confiance fort pour les fidèles ET pour un futur bailleur.
4. Le taux doit rester proche du coût réel supporté (frais marchand Orange Money/MTN eux-mêmes, autour de 1 à 3 % selon les opérateurs) — présenter ceci comme "frais de traitement du paiement mobile", pas comme une marge cachée de l'opérateur technique.

---

## 5. Projection illustrative (hypothèses, pas une promesse)

À prendre uniquement comme ordre de grandeur pour discuter avec un bailleur/investisseur — **pas des chiffres réels**, aucune donnée historique n'existe encore pour les fonder :

| Scénario | Mosquées actives | Dons moyens/mosquée/mois | Frais de service (~2 %, payés par le donateur) | Revenu plateforme/mois |
|---|---|---|---|---|
| Pilote (Phase 1) | 1-3 | 500 $ | — (numéro affiché, pas encore intégré) | 0 $ |
| Post-intégration paiement | 10 | 500 $ | 2 % | ~100 $ |
| Extension Conakry | 50 | 500 $ | 2 % | ~500 $ |
| Extension nationale | 300 | 400 $ | 2 % | ~2 400 $ |

Ces montants seuls ne financent pas une équipe à eux seuls avant l'échelle "extension nationale" — d'où l'intérêt de la subvention pour tenir la phase de construction et de croissance initiale (section 7).

---

## 6. Revenus complémentaires (une fois la base installée)

À envisager **après** la Phase 1, pas en même temps — trop de fronts ouverts à la fois nuirait au dossier Phoenix Club actuel :

- **Abonnement premium par mosquée** : fonctions avancées (écran TV, statistiques poussées, SMS pour les fidèles sans smartphone) au-delà d'un socle gratuit.
- **Parrainage/sponsoring visible sur les écrans** — déjà esquissé avec l'encart Phoenix International Club sur `/screen` : un espace "grand donateur" valorisé peut devenir une contrepartie standardisée pour de futurs bailleurs.
- **Kits matériel** (écran + boîtier type Raspberry Pi préconfiguré) vendus ou loués aux mosquées qui n'ont pas déjà d'écran — modèle déjà validé par Mawaqit sur d'autres marchés.

---

## 7. Ce qui finance quoi, et quand

```
Phoenix Club (don, en cours)
   └─> Phase 1 : pilote Conakry (1-3 mosquées), fonctionnalités actuelles + module statuts communautaires
         └─> preuve d'usage + premiers volumes de dons visibles (même sans commission)
               └─> Subvention 2 (BID / UNCDF / Orange Digital Center...) 
                     └─> Finance l'intégration paiement Orange Money/MTN MoMo (section 3)
                           └─> Commission activée, premiers revenus réels
                                 └─> Dossier investisseur crédible (traction + revenu réel)
                                       └─> Extension multi-villes / multi-pays
```

Le financement dilutif (investisseurs) arrive **après** qu'un revenu réel existe, pas avant — c'est ce qui rend le dossier finançable plutôt que spéculatif.

---

## 8. Prochaines étapes concrètes

1. Finaliser et chiffrer le budget de la Phase 1 avec le Phoenix Club (dossier `02`, section 8 — actuellement "à chiffrer").
2. Identifier 1-2 pistes de subvention en parallèle (section 2.A) pour préparer le financement de l'intégration paiement, sans attendre la fin de la Phase 1.
3. Prendre contact avec un imam/ouléma de référence pour valider le principe des frais de service (section 4) — à faire *avant* d'en parler à un bailleur, pas après.
4. Se renseigner auprès d'un conseil juridique local sur le statut réglementaire d'un agrégateur de paiement mobile money en Guinée (BCRG) avant de committer un calendrier d'intégration.
5. Une fois 1-2 mosquées actives avec des volumes réels : documenter les chiffres (fidèles inscrits, dons affichés, taux de participation aux activités) pour nourrir un futur dossier investisseur.

---

*Document préparé pour Alpha Oumar Diallo — Solutions numériques islamiques*
*Complète `01_NOTE_DE_SYNTHESE.md` et `02_DOSSIER_PROJET_COMPLET.md`*
