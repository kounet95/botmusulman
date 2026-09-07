import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Copie locale (backend/data/...) plutôt que bot/data/... : le build Docker du
# backend n'a que le dossier backend/ comme contexte (voir backend/Dockerfile,
# COPY . .) — un chemin qui remonte vers bot/ n'existe pas dans l'image et
# faisait échouer silencieusement la recherche (DATA_FILE.exists() -> False).
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "quran_pular" / "coran_versets_index.json"

DIACRITIQUES_RE = re.compile(r"[ؐ-ًؚ-ٟۖ-ۭ]")
REF_RE = re.compile(r"(\d{1,3})\s*[:,.\-/]\s*(\d{1,3})")

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

_cache = None


def _normaliser_arabe(texte: str) -> str:
    if not texte:
        return ""
    texte = DIACRITIQUES_RE.sub("", texte)
    texte = texte.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    texte = texte.replace("ى", "ي").replace("ة", "ه")
    return texte.strip()


def _charger() -> list[dict]:
    global _cache
    if _cache is None:
        if not DATA_FILE.exists():
            _cache = []
            return _cache
        with DATA_FILE.open("r", encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _obtenir_verset(sourate: int, verset: int) -> dict | None:
    for v in _charger():
        if v.get("sourate") == sourate and v.get("verset") == verset:
            return v
    return None


def _ratio_recouvrement(mots_requete: set[str], mots_cible: set[str]) -> float:
    if not mots_requete or not mots_cible:
        return 0.0
    return len(mots_requete & mots_cible) / len(mots_requete)


def rechercher_versets(q: str, n: int = 3, seuil: float = 0.45) -> list[dict]:
    q = (q or "").strip()
    if not q:
        return []

    match = REF_RE.search(q)
    if match:
        v = _obtenir_verset(int(match.group(1)), int(match.group(2)))
        if v:
            return [v]

    index = _charger()
    if not index:
        return []

    mots_arabe_requete = set(_normaliser_arabe(q).split())
    mots_requete = set(q.lower().split())

    resultats = []
    for v in index:
        score = 0.0
        if mots_arabe_requete:
            mots_arabe_verset = set(_normaliser_arabe(v.get("arabe", "")).split())
            score = max(score, _ratio_recouvrement(mots_arabe_requete, mots_arabe_verset))
        if mots_requete:
            score = max(score, _ratio_recouvrement(mots_requete, set((v.get("traduction", "") + " " + v.get("explication", "")).lower().split())))
        if score >= seuil:
            resultats.append((score, v))

    resultats.sort(key=lambda item: -item[0])
    return [v for _, v in resultats[:n]]


def match_surah_by_name(text: str) -> dict | None:
    norm = text.strip().lower()
    if len(norm) < 3:
        return None
    for i, nom in enumerate(NOMS_SOURATES, start=1):
        if nom.lower() == norm or nom.lower() in norm or norm in nom.lower():
            return {"number": i, "englishName": nom}
    return None


def format_answer(question: str, result: dict) -> str:
    explication = result.get("explication") or ""
    if len(explication) > 500:
        explication = explication[:497].rsplit(" ", 1)[0] + "…"

    lines = [
        f"📖 Sourate {result.get('sourate_nom', result.get('sourate'))} — verset {result.get('verset')}",
        "",
        result.get("arabe", ""),
        "",
        f"🔤 Pular : {result.get('traduction', '')}",
        "",
        f"📝 Explication : {explication}",
        "",
        f"source: {result.get('traduction_source', '')} / {result.get('explication_source', '')}",
    ]
    return "\n".join(lines)
