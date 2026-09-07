"""Synthèse vocale en pular via Meta MMS-TTS (auto-hébergé).

Contrairement à Whisper, Meta MMS a des modèles TTS dédiés par langue — dont
un pour le fula/fulfulde. Même approche que poular/backend/model.py (projet
Poular) : plusieurs identifiants candidats sont essayés au chargement, le
premier qui fonctionne est gardé.

"facebook/mms-tts-ful" (macro-langue fula) est confirmé public. Les variantes
dialectales (fuf = Pular/Guinée, fub, fuc, fue) peuvent nécessiter un accès
HuggingFace (HF_TOKEN) — utile si l'une d'elles donne une meilleure
prononciation pour le pular du Fuuta Djallon.
"""
import io

TTS_CANDIDATES_DEFAULT = [
    "facebook/mms-tts-ful",  # Fula (macro-langue) — confirmé public
    "facebook/mms-tts-fuf",  # Pular (Guinée / Fuuta Djallon)
    "facebook/mms-tts-fuc",
    "facebook/mms-tts-fub",
    "facebook/mms-tts-fue",
]

_model = None
_tokenizer = None
_model_id = None
_load_essaye = False


def _charger():
    global _model, _tokenizer, _model_id, _load_essaye
    if _load_essaye:
        return
    _load_essaye = True

    from config import HF_TOKEN, TTS_MODEL_ID
    from transformers import VitsModel, AutoTokenizer

    candidats = TTS_CANDIDATES_DEFAULT
    if TTS_MODEL_ID:
        candidats = [TTS_MODEL_ID] + [c for c in TTS_CANDIDATES_DEFAULT if c != TTS_MODEL_ID]
    kwargs = {"token": HF_TOKEN} if HF_TOKEN else {}

    for candidat in candidats:
        try:
            _model = VitsModel.from_pretrained(candidat, **kwargs)
            _tokenizer = AutoTokenizer.from_pretrained(candidat, **kwargs)
            _model_id = candidat
            return
        except Exception:
            continue


def preload():
    """Charge le modèle au démarrage du bot (évite la latence au premier
    utilisateur — le téléchargement initial depuis HuggingFace peut prendre
    du temps)."""
    _charger()


def disponible() -> bool:
    _charger()
    return _model is not None


def synthetiser(texte: str) -> bytes | None:
    """Génère un WAV (bytes) à partir d'un texte pular, ou None si le modèle
    est indisponible ou en cas d'erreur de synthèse."""
    _charger()
    texte = (texte or "").strip()
    if _model is None or not texte:
        return None

    import numpy as np
    import scipy.io.wavfile
    import torch

    try:
        inputs = _tokenizer(texte, return_tensors="pt")
        with torch.no_grad():
            sortie = _model(**inputs).waveform
        waveform = sortie.squeeze().numpy()

        buffer = io.BytesIO()
        scipy.io.wavfile.write(
            buffer,
            rate=_model.config.sampling_rate,
            data=(waveform * 32767).astype(np.int16),
        )
        return buffer.getvalue()
    except Exception:
        return None
