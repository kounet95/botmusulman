import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kounet:1234@postgres:5432/bot")
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

# OpenAI (transcription vocale Whisper — question coranique en poular)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Meta MMS-TTS (synthèse vocale en pular — réponse coranique en note vocale)
HF_TOKEN = os.getenv("HF_TOKEN", "")
TTS_MODEL_ID = os.getenv("TTS_MODEL_ID", "")
