"""Transcription des notes vocales via l'API Whisper (OpenAI).

Le pular/fulfulde n'est pas une langue officiellement supportée par Whisper :
la langue n'est donc pas forcée (détection automatique) et on biaise le
modèle avec un `prompt` rempli de vrais mots pular (dictionnaire + traduction
et tafsir coraniques du corpus Pular-IA) — même technique que celle utilisée
pour la transcription hors-ligne du corpus (scripts/transcription.py du
projet Pular-IA). Le résultat reste expérimental et doit être signalé comme
tel à l'utilisateur.
"""
import json
import random
from pathlib import Path

import httpx

from config import OPENAI_API_KEY

OPENAI_TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "quran_pular"
PROMPT_BASE = "Pular fulfulde fulani, langue africaine du Fuuta Djallon."
PROMPT_MAX_CHARS = 800

_prompt_cache: str | None = None


def _construire_prompt() -> str:
    """Construit le prompt Whisper à partir des vocabulaires pular disponibles
    (le dictionnaire passe en premier — mots les plus fiables/canoniques)."""
    global _prompt_cache
    if _prompt_cache is not None:
        return _prompt_cache

    fichiers = sorted(
        DATA_DIR.glob("*_vocab.json"),
        key=lambda p: 0 if p.stem.startswith("dictionnaire") else 1,
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
            return text or None
        except Exception:
            return None
