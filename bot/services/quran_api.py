"""Recherche de versets coraniques — texte arabe + traduction/tafsir en pular.

Données issues du corpus Pular-IA (traduction Rowwad Translation Center +
Tafsir Al-Mukhtasar, via quranenc.com/IslamHouse.com), pré-fusionnées verset
par verset dans data/quran_pular/coran_versets_index.json (6236 versets).

Recherche tolérante : référence "sourate:verset", ou texte libre (arabe,
français partiel dans la traduction/tafsir, ou pular) par recouvrement de
mots — fonctionne même si la requête est incomplète ou légèrement différente
du texte exact (utile pour une transcription vocale imparfaite).
"""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "quran_pular"
FICHIER_INDEX = DATA_DIR / "coran_versets_index.json"

TRADUCTION_SOURCE = "Rowwad Translation Center (traduction pular)"
EXPLICATION_SOURCE = "Tafsir Al-Mukhtasar (exégèse en pular)"

NOMS_SOURATES = [
    "Al-Fatiha", "Al-Baqarah", "Aal-E-Imran", "An-Nisa", "Al-Ma'idah",
    "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus",
    "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr",
    "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha",
    "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan",
    "Ash-Shu'ara", "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum",
    "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir",
    "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir",
    "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah",
    "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf",
    "Adh-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman",
    "Al-Waqi'ah", "Al-Hadid", "Al-Mujadilah", "Al-Hashr", "Al-Mumtahanah",
    "As-Saff", "Al-Jumu'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq",
    "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma'arij",
    "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah",
    "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "Abasa",
    "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj",
    "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad",
    "Ash-Shams", "Al-Layl", "Ad-Duha", "Ash-Sharh", "At-Tin",
    "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-Adiyat",
    "Al-Qari'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil",
    "Quraysh", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr",
    "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas",
]

_DIACRITIQUES_RE = re.compile(r"[ؐ-ًؚ-ٟۖ-ۭ]")
_REF_RE = re.compile(r"(\d{1,3})\s*[:,.\-/]\s*(\d{1,3})")

_index_liste: list[dict] | None = None
_index_dict: dict[tuple, dict] | None = None
_arabe_mots: list[frozenset] | None = None


def nom_sourate(numero: int) -> str:
    if 1 <= numero <= len(NOMS_SOURATES):
        return NOMS_SOURATES[numero - 1]
    return ""


def _normaliser_arabe(texte: str) -> str:
    if not texte:
        return ""
    texte = _DIACRITIQUES_RE.sub("", texte)
    texte = texte.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    texte = texte.replace("ى", "ي").replace("ة", "ه")
    return texte.strip()


def _charger() -> tuple[list[dict], dict[tuple, dict]]:
    """Charge et met en cache l'index des versets (appelé une seule fois)."""
    global _index_liste, _index_dict, _arabe_mots
    if _index_liste is None:
        if not FICHIER_INDEX.exists():
            _index_liste, _index_dict, _arabe_mots = [], {}, []
            return _index_liste, _index_dict
        with open(FICHIER_INDEX, encoding="utf-8") as f:
            _index_liste = json.load(f)
        _index_dict = {(v["sourate"], v["verset"]): v for v in _index_liste}
        _arabe_mots = [frozenset(_normaliser_arabe(v["arabe"]).split()) for v in _index_liste]
    return _index_liste, _index_dict


def preload():
    """Précharge l'index en mémoire (à appeler au démarrage du bot)."""
    _charger()


def obtenir_verset(sourate: int, verset: int) -> dict | None:
    _, index_dict = _charger()
    return index_dict.get((sourate, verset))


def _ratio_recouvrement(mots_requete: frozenset, mots_cible: frozenset) -> float:
    if not mots_requete or not mots_cible:
        return 0.0
    return len(mots_requete & mots_cible) / len(mots_requete)


def rechercher_versets(q: str, n: int = 5, seuil: float = 0.6) -> list[dict]:
    """Référence "2:255" → verset précis. Sinon texte libre (arabe, français/pular
    dans la traduction ou le tafsir) → recouvrement de mots, tolérant aux
    formulations incomplètes ou approximatives (utile pour la voix)."""
    q = (q or "").strip()
    if not q:
        return []

    m = _REF_RE.search(q)
    if m:
        v = obtenir_verset(int(m.group(1)), int(m.group(2)))
        if v:
            return [v]

    index_liste, _ = _charger()
    if not index_liste:
        return []

    mots_arabe_requete = frozenset(_normaliser_arabe(q).split())
    mots_requete = frozenset(q.lower().split())

    resultats = []
    for v, mots_arabe_verset in zip(index_liste, _arabe_mots):
        score = 0.0
        if mots_arabe_requete:
            score = max(score, _ratio_recouvrement(mots_arabe_requete, mots_arabe_verset))
        if mots_requete:
            score = max(score, _ratio_recouvrement(mots_requete, frozenset(v["traduction"].lower().split())))
            score = max(score, _ratio_recouvrement(mots_requete, frozenset(v["explication"].lower().split())))
        if score >= seuil:
            resultats.append((score, v))

    resultats.sort(key=lambda t: -t[0])
    return [v for _, v in resultats[:n]]


def match_surah_by_name(text: str) -> dict | None:
    """Fait correspondre un nom de sourate (souvent un emprunt arabe, donc
    reconnaissable même en poular) à son numéro — pour lister une sourate
    entière sans préciser de verset."""
    norm = text.strip().lower()
    if len(norm) < 3:
        return None
    for i, nom in enumerate(NOMS_SOURATES, start=1):
        if nom.lower() == norm or nom.lower() in norm or norm in nom.lower():
            return {"number": i, "englishName": nom}
    return None
