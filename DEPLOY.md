# CI/CD — Build & déploiement continu

## Ce qui est en place

- **`.github/workflows/ci.yml`** — à chaque push/PR : build des 3 images Docker (backend, bot, dashboard) pour valider que tout compile. Aucun déploiement.
- **`.github/workflows/deploy.yml`** — à chaque push sur `main` :
  1. Build et publie les 3 images sur GitHub Container Registry (`ghcr.io/kounet95/botmusulman-{backend,bot,dashboard}`), taguées `latest` et par commit SHA.
  2. Si le déploiement est activé (voir ci-dessous), se connecte en SSH au serveur et relance la stack avec les nouvelles images.

Le build/push GHCR fonctionne dès maintenant, sans rien à configurer (utilise le `GITHUB_TOKEN` automatique). Le déploiement SSH est **désactivé par défaut** tant que les secrets ci-dessous ne sont pas renseignés.

## Activer le déploiement automatique

Dans **Settings → Secrets and variables → Actions** du repo GitHub :

**Secrets** (Settings → Secrets and variables → Actions → *Secrets*) :
- `DEPLOY_HOST` — IP ou nom d'hôte du serveur de production
- `DEPLOY_USER` — utilisateur SSH
- `DEPLOY_SSH_KEY` — clé privée SSH (le serveur doit avoir la clé publique correspondante dans `~/.ssh/authorized_keys`)
- `DEPLOY_PORT` — port SSH (optionnel, 22 par défaut)
- `DEPLOY_PATH` — chemin absolu du repo cloné sur le serveur (ex: `/home/deploy/botmusulman`)

**Variables** (même écran, onglet *Variables*) :
- `DEPLOY_ENABLED` = `true`

Le serveur doit avoir : Docker + Docker Compose installés, et un `git clone` du repo avec un `.env` déjà configuré (jamais commité, à copier manuellement une fois lors de la mise en place du serveur).

## Rotation de secrets — À FAIRE MANUELLEMENT

`.env` a été committé par erreur puis retiré du suivi Git. Les valeurs qu'il contenait doivent être considérées comme compromises (elles restent visibles dans l'historique Git déjà poussé) :

1. **Token Telegram** : revoke + régénère via [@BotFather](https://t.me/BotFather) (`/revoke`, puis `/token`), mets à jour `TELEGRAM_BOT_TOKEN` dans le `.env` du serveur, redémarre le service `bot`.
2. **API_SECRET_KEY** : déjà régénérée localement dans ce projet — reporte la même nouvelle valeur dans le `.env` du serveur de production (invalide les sessions actives, une reconnexion suffit).
