-- MosquéeBot — Schéma Supabase
-- Copiez-collez ce SQL dans l'éditeur SQL de votre projet Supabase

-- ── Mosquées ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mosques (
  id           SERIAL PRIMARY KEY,
  name         TEXT NOT NULL,
  city         TEXT NOT NULL DEFAULT 'Gatineau',
  country      TEXT NOT NULL DEFAULT 'CA',
  admin_telegram_id TEXT,
  bot_token    TEXT,
  slug         TEXT UNIQUE,
  -- Profil "Mawaqit" complété lors de l'onboarding post-inscription
  installation_type    TEXT DEFAULT 'mosque', -- mosque | ecole | salle_priere | domicile | magasin
  address              TEXT,
  postal_code          TEXT,
  association_name     TEXT,
  phone                TEXT,
  email                TEXT,
  website              TEXT,
  payment_url          TEXT,
  amenities            TEXT[] DEFAULT '{}',
  construction_year    INTEGER,
  capacity_women       INTEGER,
  capacity_men         INTEGER,
  history              TEXT,
  other_info           TEXT,
  exterior_photo_url   TEXT,
  interior_photo_url   TEXT,
  logo_url             TEXT,
  onboarding_completed BOOLEAN DEFAULT TRUE,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Mosquée démo par défaut
INSERT INTO mosques (name, city, country, slug)
VALUES ('Mosquée Al-Nour — Démo', 'Gatineau', 'CA', 'mosquee-al-nour-demo')
ON CONFLICT DO NOTHING;

-- ── Comptes admin (un compte = un accès dashboard pour une mosquée) ──
CREATE TABLE IF NOT EXISTS admin_users (
  id            SERIAL PRIMARY KEY,
  mosque_id     INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name     TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ── Membres ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
  id           SERIAL PRIMARY KEY,
  mosque_id    INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  telegram_id  TEXT UNIQUE NOT NULL,
  first_name   TEXT NOT NULL DEFAULT '',
  username     TEXT DEFAULT '',
  joined_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_members_mosque ON members(mosque_id);
CREATE INDEX IF NOT EXISTS idx_members_telegram ON members(telegram_id);

-- ── Préférences de notifications ────────────────────────────
CREATE TABLE IF NOT EXISTS notification_preferences (
  id           SERIAL PRIMARY KEY,
  member_id    INTEGER UNIQUE REFERENCES members(id) ON DELETE CASCADE,
  prayer_times BOOLEAN DEFAULT TRUE,
  jumua        BOOLEAN DEFAULT TRUE,
  courses      BOOLEAN DEFAULT TRUE,
  conferences  BOOLEAN DEFAULT TRUE,
  announcements BOOLEAN DEFAULT TRUE,
  hajj_umrah   BOOLEAN DEFAULT TRUE
);

-- ── Activités ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activities (
  id               SERIAL PRIMARY KEY,
  mosque_id        INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  title            TEXT NOT NULL,
  description      TEXT,
  type             TEXT NOT NULL DEFAULT 'cours',  -- cours | conference | halaqa | evenement | autre
  date             DATE NOT NULL,
  time             TIME NOT NULL,
  capacity         INTEGER NOT NULL DEFAULT 30,
  registered_count INTEGER NOT NULL DEFAULT 0,
  is_paid          BOOLEAN DEFAULT FALSE,
  price            DECIMAL(10,2),
  speaker          TEXT,
  location         TEXT DEFAULT 'Mosquée',
  livestream_url   TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activities_mosque_date ON activities(mosque_id, date);

-- Données de démo
INSERT INTO activities (mosque_id, title, type, date, time, capacity, registered_count, speaker, location, description)
VALUES
  (1, 'Cours de Tajwid — Niveau débutant', 'cours', CURRENT_DATE + INTERVAL '3 days', '19:00', 20, 12, 'Ustaz Ibrahim', 'Salle principale', 'Apprentissage de la récitation coranique avec les règles du Tajwid.'),
  (1, 'Conférence : La miséricorde dans l''Islam', 'conference', CURRENT_DATE + INTERVAL '7 days', '15:00', 100, 45, 'Cheikh Moussa Konaté', 'Grande salle', 'Une conférence sur les valeurs de miséricorde et de compassion dans la tradition islamique.'),
  (1, 'Halaqa femmes — Sira du Prophète ﷺ', 'halaqa', CURRENT_DATE + INTERVAL '5 days', '14:00', 15, 8, NULL, 'Salle des femmes', NULL),
  (1, 'Séminaire : Fiqh des finances halal', 'conference', CURRENT_DATE + INTERVAL '14 days', '10:00', 50, 30, 'Dr. Ibrahim Al-Masri', 'Salle principale', NULL);

-- ── Inscriptions ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS registrations (
  id          SERIAL PRIMARY KEY,
  activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
  member_id   INTEGER REFERENCES members(id) ON DELETE CASCADE,
  attended    BOOLEAN DEFAULT FALSE,
  registered_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(activity_id, member_id)
);

CREATE INDEX IF NOT EXISTS idx_registrations_activity ON registrations(activity_id);
CREATE INDEX IF NOT EXISTS idx_registrations_member ON registrations(member_id);

-- ── Liste d'attente ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS waitlist (
  id          SERIAL PRIMARY KEY,
  activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
  member_id   INTEGER REFERENCES members(id) ON DELETE CASCADE,
  added_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(activity_id, member_id)
);

-- ── Contenu programmé ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_schedule (
  id             SERIAL PRIMARY KEY,
  mosque_id      INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  type           TEXT NOT NULL,  -- hadith | verset | rappel | dua
  content_ar     TEXT,
  content_fr     TEXT,
  content_en     TEXT,
  source         TEXT,
  scheduled_date DATE NOT NULL,
  sent_at        TIMESTAMPTZ,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Hadiths de démo pour les 7 prochains jours
INSERT INTO content_schedule (mosque_id, type, content_fr, source, scheduled_date) VALUES
  (1, 'hadith', 'Le Prophète ﷺ a dit : « Celui qui croit en Allah et au Jour dernier doit honorer son voisin. »', 'Bukhari & Muslim', CURRENT_DATE),
  (1, 'hadith', 'Le Prophète ﷺ a dit : « Les actions ne valent que par leurs intentions. »', 'Bukhari', CURRENT_DATE + 1),
  (1, 'hadith', 'Le Prophète ﷺ a dit : « Le sourire à ton frère est une sadaqa. »', 'Tirmidhi', CURRENT_DATE + 2),
  (1, 'hadith', 'Le Prophète ﷺ a dit : « Aucun de vous n''est vraiment croyant tant qu''il n''aime pas pour son frère ce qu''il aime pour lui-même. »', 'Bukhari & Muslim', CURRENT_DATE + 3),
  (1, 'verset', 'Certes, avec la difficulté vient la facilité.', 'Sourate Al-Inshirah (94:6)', CURRENT_DATE + 4),
  (1, 'hadith', 'Le Prophète ﷺ a dit : « La meilleure des aumônes est celle que donne celui qui a peu. »', 'Abu Dawud', CURRENT_DATE + 5),
  (1, 'rappel', 'Prenez soin de vos parents. Leur satisfaction est la satisfaction d''Allah.', NULL, CURRENT_DATE + 6);

-- ── Collectes de dons ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS donation_campaigns (
  id               SERIAL PRIMARY KEY,
  mosque_id        INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  title            TEXT NOT NULL,
  description      TEXT,
  type             TEXT DEFAULT 'general',
  goal_amount      DECIMAL(12,2),
  collected_amount DECIMAL(12,2) DEFAULT 0,
  payment_url      TEXT,
  orange_money_number TEXT,
  mtn_momo_number  TEXT,
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Campagnes de démo
INSERT INTO donation_campaigns (mosque_id, title, type, goal_amount, collected_amount, payment_url) VALUES
  (1, 'Don général mosquée', 'general', NULL, 0, NULL),
  (1, 'Rénovation salle de prière', 'projet', 15000, 8420, NULL),
  (1, 'Bourse étudiants musulmans', 'bourse', 5000, 2100, NULL);

-- ── Annonces ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS announcements (
  id         SERIAL PRIMARY KEY,
  mosque_id  INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  body       TEXT NOT NULL,
  sent_at    TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Row Level Security (optionnel pour prod) ─────────────────
-- ALTER TABLE members ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
-- (Configurer selon vos besoins de sécurité)

-- ── Multi-tenant : slug de mosquée + comptes admin ───────────
ALTER TABLE mosques ADD COLUMN IF NOT EXISTS slug TEXT UNIQUE;
UPDATE mosques SET slug = 'al-nour-demo' WHERE id = 1 AND slug IS NULL;

CREATE TABLE IF NOT EXISTS admin_users (
  id            SERIAL PRIMARY KEY,
  mosque_id     INTEGER UNIQUE REFERENCES mosques(id) ON DELETE CASCADE,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name     TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
