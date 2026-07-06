from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import upsert_member, get_member, get_mosque, get_mosque_by_slug, list_mosques


def _main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🕌 Horaires de prière", callback_data="menu_prayer"),
            InlineKeyboardButton("📅 Activités", callback_data="menu_activities"),
        ],
        [
            InlineKeyboardButton("📖 Mes cours", callback_data="menu_my_courses"),
            InlineKeyboardButton("🤲 Dons", callback_data="menu_donations"),
        ],
        [
            InlineKeyboardButton("🔔 Mes notifications", callback_data="menu_notifications"),
            InlineKeyboardButton("ℹ️ À propos", callback_data="menu_about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def _mosque_picker_markup(mosques: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"🕌 {m['name']} — {m['city']}", callback_data=f"pick_mosque_{m['id']}")]
        for m in mosques
    ]
    return InlineKeyboardMarkup(buttons)


async def _greet(send, first_name: str, mosque_name: str | None):
    text = (
        f"*Assalamu alaykum, {first_name}! 🌙*\n\n"
        + (f"Bienvenue sur le bot de *{mosque_name}*.\n\n" if mosque_name else "Bienvenue sur le bot de votre mosquée.\n\n")
        + "Que puis-je faire pour vous aujourd'hui ?"
    )
    await send(text, parse_mode="Markdown", reply_markup=_main_menu_markup())


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    mosque = None
    if context.args:
        mosque = await get_mosque_by_slug(context.args[0])

    if mosque:
        await upsert_member(user.id, user.first_name, user.username, mosque["id"])
        await _greet(update.message.reply_text, user.first_name, mosque["name"])
        return

    existing = await get_member(user.id)
    if existing and existing.get("mosque_id"):
        await _greet(update.message.reply_text, user.first_name, None)
        return

    mosques = await list_mosques()
    if not mosques:
        await update.message.reply_text("❌ Aucune mosquée n'est encore enregistrée sur ce bot.")
        return

    await update.message.reply_text(
        f"*Assalamu alaykum, {user.first_name}! 🌙*\n\n"
        "Choisissez votre mosquée pour continuer :",
        parse_mode="Markdown",
        reply_markup=_mosque_picker_markup(mosques),
    )


async def cb_pick_mosque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    mosque_id = int(query.data.split("_")[-1])

    mosque = await get_mosque(mosque_id)
    if not mosque:
        await query.edit_message_text("❌ Mosquée introuvable.")
        return

    await upsert_member(user.id, user.first_name, user.username, mosque_id)
    await _greet(query.edit_message_text, user.first_name, mosque["name"])


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("*Menu principal* 🌙", parse_mode="Markdown", reply_markup=_main_menu_markup())


async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "ℹ️ *À propos de ce bot*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Ce bot a été développé par *Alpha Oumar Diallo*\n"
        "Développeur de solutions numériques islamiques\n\n"
        "📱 Services disponibles :\n"
        "• Horaires de prière automatiques\n"
        "• Inscriptions aux cours & conférences\n"
        "• Rappels personnalisés\n"
        "• Collecte de dons\n"
        "• Annonces de la mosquée\n\n"
        "💬 Contact : @alphaoumardiallo\n"
        "🌐 Pour votre mosquée : contactez-nous\n\n"
        "_Barakallahu fik_ 🤲"
    )
    await query.edit_message_text(text, parse_mode="Markdown")
