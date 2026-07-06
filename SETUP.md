# MosquéeBot — Guide de démarrage

## 1. Créer le bot Telegram

1. Ouvre Telegram → cherche **@BotFather**
2. Tape `/newbot` → donne un nom → ex: `Mosquée Al-Nour`
3. Donne un username → ex: `mosqueealnour_bot`
4. Copie le **token** que BotFather t'envoie

## 2. Créer le projet Supabase

1. Va sur [supabase.com](https://supabase.com) → New Project
2. Donne un nom : `mosqueebot`
3. Copie l'**URL** et la clé **anon** (Settings → API)
4. Va dans **SQL Editor** → colle le contenu de `database/schema.sql` → Run

## 3. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Remplis le fichier `.env` :
```
TELEGRAM_BOT_TOKEN=ton_token_botfather
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=ta_cle_anon
```

## 4. Démarrer avec Docker

```bash
docker-compose up -d
```

Le bot sera actif, l'API sur `http://localhost:8000`, le dashboard sur `http://localhost:80`.

## 5. Sans Docker (développement local)

### Bot
```bash
cd bot
pip install -r requirements.txt
python main.py
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Dashboard
Ouvre simplement `dashboard/index.html` dans un navigateur.

## Commandes du bot

| Commande | Action |
|----------|--------|
| `/start` | Bienvenue + menu principal |
| `/prieres` | Horaires de prière du jour |
| `/prochaine` | Prochaine prière |
| `/activites` | Liste des activités à venir |
| `/dons` | Collectes de dons actives |
| `/menu` | Retour au menu principal |

## Structure du projet

```
botmusulman/
├── bot/              ← Bot Telegram (Python)
│   ├── handlers/     ← Commandes et callbacks
│   ├── services/     ← API prières, Supabase, scheduler
│   └── main.py       ← Point d'entrée
├── backend/          ← API REST (FastAPI)
│   ├── routers/      ← Routes par module
│   └── main.py       ← Point d'entrée
├── dashboard/        ← Interface admin (HTML/CSS/JS)
│   ├── index.html    ← Page principale
│   ├── css/          ← Styles
│   └── js/           ← Logique frontend
├── database/
│   └── schema.sql    ← Schéma Supabase
├── docker-compose.yml
└── .env.example
```

## Personnaliser pour une mosquée

Dans `bot/config.py`, change :
```python
DEFAULT_CITY = "Gatineau"     # ← ville de la mosquée
DEFAULT_COUNTRY = "CA"        # ← code pays (CA, GN, SN, FR...)
```

Dans `dashboard/index.html`, ligne 10 :
```js
window.MOSQUE_ID = 1;  // ID de la mosquée dans Supabase
```

---

Développé par **Alpha Oumar Diallo** — Solutions numériques islamiques  
Contact : @alphaoumardiallo | kounetdiallo95@gmail.com
