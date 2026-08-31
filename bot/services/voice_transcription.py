"""Transcription des notes vocales via l'API Whisper (OpenAI).

Le pular/fulfulde n'est pas une langue officiellement supportée par Whisper,
donc deux techniques exploitent le corpus pular (dictionnaire + traduction et
tafsir coraniques) pour compenser :

1. Avant la transcription : le modèle est biaisé avec un `prompt` rempli de
   vrais mots pular (même technique que scripts/transcription.py du projet
   Pular-IA).
2. Après la transcription : chaque mot du résultat qui ne correspond à aucun
   mot connu du corpus est comparé à l'ensemble du vocabulaire pular et
   "recollé" au mot le plus proche si la ressemblance est forte — une
   correction orthographique par dictionnaire, impossible à faire pendant la
   transcription elle-même (le prompt biaise, mais ne corrige pas).

Le résultat reste expérimental et doit être signalé comme tel à l'utilisateur.
"""
import difflib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

import httpx

from config import OPENAI_API_KEY

OPENAI_TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "quran_pular"
PROMPT_BASE = "Pular fulfulde fulani, langue africaine du Fuuta Djallon."
PROMPT_MAX_CHARS = 800

# Correction : un mot inconnu doit ressembler à au moins ce ratio pour être
# remplacé — volontairement strict pour ne pas corrompre les mots français/
# arabes (Allah, sourate, numéros...) que l'utilisateur peut mélanger au pular.
CORRECTION_CUTOFF = 0.82
CORRECTION_LONGUEUR_MIN = 4

_prompt_cache: str | None = None
_vocab_complet: list[str] | None = None
_vocab_set: set[str] | None = None
_vocab_par_lettre: dict[str, list[str]] | None = None

_MOT_RE = re.compile(r"[^\wɓɗƴŋ'-]", re.UNICODE)


def _charger_vocab_fichiers(tri_dictionnaire_dabord: bool) -> list[str]:
    fichiers = sorted(
        DATA_DIR.glob("*_vocab.json"),
        key=(lambda p: 0 if p.stem.startswith("dictionnaire") else 1) if tri_dictionnaire_dabord else (lambda p: p.stem),
    )
    mots, vus = [], set()
    for fichier in fichiers:
        try:
            with open(fichier, encoding="utf-8") as f:
                for mot in json.load(f):
                    if mot not in vus:
                        vus.add(mot)
                        mots.append(mot)
        except Exception:
            continue
    return mots


def _construire_prompt() -> str:
    """Construit le prompt Whisper (le dictionnaire passe en premier — mots
    les plus fiables/canoniques). Limité par la taille max acceptée par
    l'API (~quelques centaines de caractères utiles)."""
    global _prompt_cache
    if _prompt_cache is not None:
        return _prompt_cache

    mots = _charger_vocab_fichiers(tri_dictionnaire_dabord=True)
    if not mots:
        _prompt_cache = PROMPT_BASE
        return _prompt_cache

    random.Random(42).shuffle(mots)  # échantillon fixe, reproductible

    prompt = PROMPT_BASE
    for mot in mots:
        candidat = f"{prompt} {mot}"
        if len(candidat) > PROMPT_MAX_CHARS:
            break
        prompt = candidat

    _prompt_cache = prompt
    return _prompt_cache


def _index_correction():
    """Charge tout le vocabulaire pular (~dizaines de milliers de mots) et
    l'indexe par première lettre pour une correction rapide."""
    global _vocab_complet, _vocab_set, _vocab_par_lettre
    if _vocab_set is not None:
        return

    mots = [m.strip().lower() for m in _charger_vocab_fichiers(tri_dictionnaire_dabord=False) if m.strip()]
    _vocab_complet = mots
    _vocab_set = set(mots)
    _vocab_par_lettre = defaultdict(list)
    for m in mots:
        _vocab_par_lettre[m[0]].append(m)


def corriger_transcription(texte: str) -> str:
    """Corrige les mots du transcript qui ressemblent fortement à un mot
    connu du dictionnaire/corpus pular mais ne correspondent pas exactement
    (orthographe approximative — attendu pour une langue non supportée
    nativement par Whisper). Les mots déjà connus, trop courts, ou sans
    correspondance suffisamment proche sont laissés tels quels."""
    if not texte:
        return texte

    _index_correction()
    if not _vocab_set:
        return texte

    mots_corriges = []
    for mot in texte.split():
        normalise = _MOT_RE.sub("", mot).lower()
        if len(normalise) < CORRECTION_LONGUEUR_MIN or normalise in _vocab_set:
            mots_corriges.append(mot)
            continue

        candidats = [c for c in _vocab_par_lettre.get(normalise[0], []) if abs(len(c) - len(normalise)) <= 2]
        proche = difflib.get_close_matches(normalise, candidats, n=1, cutoff=CORRECTION_CUTOFF)
        mots_corriges.append(proche[0] if proche else mot)

    return " ".join(mots_corriges)


async def transcribe_voice(audio_bytes: bytes, filename: str = "voice.ogg") -> str | None:
    if not OPENAI_API_KEY:
        return None

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": (filename, audio_bytes, "audio/ogg")}
    data = {"model": "whisper-1", "prompt": _construire_prompt()}

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(OPENAI_TRANSCRIBE_URL, headers=headers, files=files, data=data)
            r.raise_for_status()
            text = r.json().get("text", "").strip()
            if not text:
                return None
            return corriger_transcription(text)
        except Exception:
            return None
