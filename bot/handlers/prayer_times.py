from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.prayer_api import get_prayer_times, format_prayer_times, get_next_prayer
from services.mosque_context import resolve_user_mosque

NO_MOSQUE_TEXT = "❌ Vous n'êtes rattaché(e) à aucune mosquée. Tapez /start pour en choisir une."


def _location_label(mosque: dict) -> str:
    if mosque.get("neighborhood"):
        return f"{mosque['city']}, {mosque['neighborhood']}"
    return mosque["city"]


async def cmd_prieres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await update.message.reply_text(NO_MOSQUE_TEXT)
        return

    await update.message.reply_text("⏳ Récupération des horaires...")

    timings = await get_prayer_times(mosque["city"], mosque["country"])
    if not timings:
        text = "❌ Impossible de récupérer les horaires. Réessayez plus tard."
    else:
        text = format_prayer_times(timings, _location_label(mosque))

    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu_main")]]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def cb_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await query.edit_message_text(NO_MOSQUE_TEXT)
        return

    timings = await get_prayer_times(mosque["city"], mosque["country"])
    if not timings:
        text = "❌ Impossible de récupérer les horaires. Réessayez plus tard."
    else:
        text = format_prayer_times(timings, _location_label(mosque))
    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu_main")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def cmd_prochaine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await update.message.reply_text(NO_MOSQUE_TEXT)
        return

    result = await get_next_prayer(mosque["city"], mosque["country"])
    if not result:
        await update.message.reply_text("❌ Impossible de récupérer les horaires.")
        return
    name, time = result
    emoji_map = {"Fajr": "🌙", "Dhuhr": "☀️", "Asr": "🌤️", "Maghrib": "🌇", "Isha": "🌙"}
    emoji = emoji_map.get(name, "🕌")
    text = (
        f"⏰ *Prochaine prière*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} *{name}* à *{time}*\n\n"
        f"_Préparez-vous pour la prière_ 🤲"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
