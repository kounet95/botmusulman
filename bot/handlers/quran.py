import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.quran_api import rechercher_versets, match_surah_by_name
from services.voice_transcription import transcribe_voice
from services import quran_tts

_BACK_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_main")]])

INTRO_TEXT = (
    "📖 *Question coranique*\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "Posez votre question *en texte ou en note vocale* — en poular, en français "
    "ou en arabe 🎙️\n\n"
    "Exemples :\n"
    "• _2:255_ (référence sourate:verset)\n"
    "• _Al-Fatiha_\n"
    "• un mot ou une phrase, en poular ou en français : _munyal_ (patience), "
    "_zakat_, _yaafuya_ (pardon)...\n\n"
    "⚠️ _La reconnaissance vocale en poular reste expérimentale : "
    "si la transcription est incorrecte, réessayez ou reformulez._"
)

NOT_FOUND_TEXT = (
    "❌ Aucun verset trouvé.\n\n"
    "Essayez :\n"
    "• une référence : _2:255_\n"
    "• un nom de sourate : _Al-Baqara_\n"
    "• un mot-clé plus simple, en poular ou en français"
)

MAX_EXPLICATION_CHARS = 500


async def cmd_coran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_quran_query"] = True
    await update.message.reply_text(INTRO_TEXT, parse_mode="Markdown", reply_markup=_BACK_MARKUP)


async def cb_quran_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_quran_query"] = True
    await query.edit_message_text(INTRO_TEXT, parse_mode="Markdown", reply_markup=_BACK_MARKUP)


def _format_ayah(v: dict) -> str:
    explication = v.get("explication") or ""
    if len(explication) > MAX_EXPLICATION_CHARS:
        explication = explication[:MAX_EXPLICATION_CHARS].rsplit(" ", 1)[0] + "…"

    lines = [
        f"📖 *Sourate {v['sourate_nom']} — verset {v['verset']}*",
        "━━━━━━━━━━━━━━━━━━",
        "",
        v["arabe"],
        "",
        f"🔤 *Pular* — {v['traduction']}",
    ]
    if explication:
        lines += ["", f"📝 *Tafsir* — {explication}"]
    lines += ["", f"_Source : {v['traduction_source']} · {v['explication_source']}_"]
    return "\n".join(lines)


def _format_results(results: list[dict], keyword: str) -> str:
    lines = [f"🔍 *Résultats pour « {keyword} »*", "━━━━━━━━━━━━━━━━━━"]
    for v in results:
        lines.append(f"\n📖 *{v['sourate_nom']} {v['sourate']}:{v['verset']}*\n{v['arabe']}\n🔤 {v['traduction']}")
    return "\n".join(lines)


async def _envoyer_audio(message, texte: str):
    """Synthèse vocale en pular (Meta MMS-TTS, auto-hébergé) de la réponse.
    Silencieux si le modèle est indisponible — la réponse texte suffit alors."""
    if not quran_tts.disponible():
        return
    audio = await asyncio.to_thread(quran_tts.synthetiser, texte)
    if audio:
        await message.reply_audio(audio, filename="reponse.wav", title="Réponse coranique (pular)")


async def _answer_query(message, query_text: str):
    query_text = query_text.strip()
    if not query_text:
        await message.reply_text("❌ Je n'ai pas compris la question. Réessayez.", parse_mode="Markdown", reply_markup=_BACK_MARKUP)
        return

    results = rechercher_versets(query_text, n=5)
    if len(results) == 1:
        v = results[0]
        await message.reply_text(_format_ayah(v), parse_mode="Markdown", reply_markup=_BACK_MARKUP)
        await _envoyer_audio(message, v["traduction"])
        return
    if results:
        await message.reply_text(_format_results(results, query_text), parse_mode="Markdown", reply_markup=_BACK_MARKUP)
        return

    surah = match_surah_by_name(query_text)
    if surah:
        text = (
            f"📖 *Sourate {surah['englishName']} ({surah['number']})*\n\n"
            f"Précisez un verset, ex : _{surah['number']}:1_"
        )
        await message.reply_text(text, parse_mode="Markdown", reply_markup=_BACK_MARKUP)
        return

    await message.reply_text(NOT_FOUND_TEXT, parse_mode="Markdown", reply_markup=_BACK_MARKUP)


async def handle_text_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_quran_query"):
        return
    await _answer_query(update.message, update.message.text)


async def handle_voice_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        return

    processing = await update.message.reply_text("🎙️ Transcription de votre question...")
    file = await context.bot.get_file(voice.file_id)
    audio_bytes = bytes(await file.download_as_bytearray())
    transcript = await transcribe_voice(audio_bytes)

    if not transcript:
        await processing.edit_text(
            "❌ Impossible de transcrire la note vocale. Réessayez ou posez votre question par texte.",
            reply_markup=_BACK_MARKUP,
        )
        return

    context.user_data["awaiting_quran_query"] = True
    await processing.edit_text(f"🗣️ Compris : « {transcript} »")
    await _answer_query(update.message, transcript)
