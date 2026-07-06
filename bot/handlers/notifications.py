from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import get_member_prefs, update_member_pref

PREFS = [
    ("prayer_times", "Horaires de prière",         "🕌"),
    ("jumua",        "Rappel Jumu'a",               "🕋"),
    ("courses",      "Rappels cours & activités",   "🎓"),
    ("conferences",  "Conférences & événements",    "🎤"),
    ("hajj_umrah",   "Hajj & Omra",                 "🕋"),
    ("announcements","Annonces & hadiths",           "📢"),
]


async def cb_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    prefs = await get_member_prefs(user.id)
    text, markup = _build_notif_menu(prefs)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


def _build_notif_menu(prefs: dict):
    text = (
        "🔔 *Mes notifications*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Activez ou désactivez vos préférences :"
    )
    buttons = []
    for key, label, emoji in PREFS:
        is_on = prefs.get(key, True)
        status = "✅" if is_on else "❌"
        buttons.append([InlineKeyboardButton(
            f"{status} {emoji} {label}",
            callback_data=f"notif_toggle_{key}",
        )])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_main")])
    return text, InlineKeyboardMarkup(buttons)


async def cb_toggle_notif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    pref_key = query.data.replace("notif_toggle_", "")
    # Validation : n'accepter que les clés connues
    allowed = {k for k, _, _ in PREFS}
    if pref_key not in allowed:
        return
    prefs = await get_member_prefs(user.id)
    new_value = not prefs.get(pref_key, True)
    await update_member_pref(user.id, pref_key, new_value)
    prefs[pref_key] = new_value
    text, markup = _build_notif_menu(prefs)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
