from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import (
    get_upcoming_activities, get_activity, register_to_activity,
    unregister_from_activity, get_member_registrations, is_member_registered,
)
from services.mosque_context import resolve_user_mosque

NO_MOSQUE_TEXT = "❌ Vous n'êtes rattaché(e) à aucune mosquée. Tapez /start pour en choisir une."

ACTIVITY_TYPE_EMOJI = {
    "cours":      "🎓",
    "conference": "🎤",
    "halaqa":     "📖",
    "evenement":  "🗓️",
    "autre":      "🌟",
}

FILTER_LABELS = {
    "all":        "📅 Tout",
    "cours":      "🎓 Cours",
    "conference": "🎤 Conf.",
    "halaqa":     "📖 Halaqa",
    "evenement":  "🗓️ Événements",
}


def _filter_from_callback(data: str) -> str:
    suffix = data.replace("menu_activities", "").lstrip("_")
    return suffix if suffix in FILTER_LABELS else "all"


def _activity_list_text(activities: list[dict], active_filter: str = "all") -> str:
    label = FILTER_LABELS.get(active_filter, "📅 Tout")
    header = f"📅 *Activités à venir* — {label}"
    if not activities:
        return (
            f"{header}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Aucune activité prévue dans cette catégorie.\n"
            "Revenez bientôt ! 🌙"
        )
    lines = [header, "━━━━━━━━━━━━━━━━━━"]
    for act in activities:
        emoji = ACTIVITY_TYPE_EMOJI.get(act.get("type", "autre"), "🌟")
        price_str = "Gratuit" if not act.get("is_paid") else f"{act.get('price', '?')}$"
        spots = act.get("capacity", 0) - act.get("registered_count", 0)
        spot_warn = " ⚠️ Presque complet" if 0 < spots <= 5 else (" 🔴 Complet" if spots <= 0 else "")
        lines.append(
            f"\n{emoji} *{act['title']}*\n"
            f"   📅 {act['date']} à {act['time']}\n"
            f"   👥 {act.get('registered_count', 0)}/{act.get('capacity', '?')} places | {price_str}{spot_warn}"
        )
    lines.append("\n━━━━━━━━━━━━━━━━━━")
    lines.append("_Appuyez sur une activité pour vous inscrire._")
    return "\n".join(lines)


def _activity_keyboard(activities: list[dict], active_filter: str = "all") -> InlineKeyboardMarkup:
    buttons = []

    # Filter buttons — 3 par ligne
    filter_items = list(FILTER_LABELS.items())
    for i in range(0, len(filter_items), 3):
        row = []
        for key, label in filter_items[i:i + 3]:
            cb = "menu_activities" if key == "all" else f"menu_activities_{key}"
            prefix = "▶ " if key == active_filter else ""
            row.append(InlineKeyboardButton(f"{prefix}{label}", callback_data=cb))
        buttons.append(row)

    # Boutons activités
    for act in activities:
        emoji = ACTIVITY_TYPE_EMOJI.get(act.get("type", "autre"), "🌟")
        spots = act.get("capacity", 0) - act.get("registered_count", 0)
        spot_icon = " ⚠️" if 0 < spots <= 5 else (" 🔴" if spots <= 0 else "")
        buttons.append([InlineKeyboardButton(
            f"{emoji} {act['title'][:38]}{spot_icon}",
            callback_data=f"act_detail_{act['id']}",
        )])

    buttons.append([
        InlineKeyboardButton("📖 Mes inscriptions", callback_data="menu_my_courses"),
        InlineKeyboardButton("🔙 Menu", callback_data="menu_main"),
    ])
    return InlineKeyboardMarkup(buttons)


# ── Commandes & callbacks ────────────────────────────────────────────────────

async def cmd_activites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await update.message.reply_text(NO_MOSQUE_TEXT)
        return
    activities = await get_upcoming_activities(mosque["id"])
    text = _activity_list_text(activities)
    markup = _activity_keyboard(activities)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)


async def cb_activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await query.edit_message_text(NO_MOSQUE_TEXT)
        return
    active_filter = _filter_from_callback(query.data)
    type_filter = None if active_filter == "all" else active_filter
    activities = await get_upcoming_activities(mosque["id"], type_filter)
    text = _activity_list_text(activities, active_filter)
    markup = _activity_keyboard(activities, active_filter)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def cb_activity_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity_id = int(query.data.split("_")[-1])
    act = await get_activity(activity_id)
    if not act:
        await query.edit_message_text("❌ Activité introuvable.")
        return

    user = update.effective_user
    registered = await is_member_registered(user.id, activity_id)

    emoji = ACTIVITY_TYPE_EMOJI.get(act.get("type", "autre"), "🌟")
    spots_left = act.get("capacity", 0) - act.get("registered_count", 0)
    price_str = "Gratuit 🎁" if not act.get("is_paid") else f"{act.get('price', '?')}$ 💳"

    text = (
        f"{emoji} *{act['title']}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📅 {act['date']} à {act['time']}\n"
        f"📍 {act.get('location', 'Mosquée')}\n"
        f"💰 {price_str}\n"
        f"👥 {act.get('registered_count', 0)}/{act.get('capacity', '?')} inscrits"
        f"{' | ⚠️ Presque complet !' if spots_left <= 5 and spots_left > 0 else (' | 🔴 Complet' if spots_left <= 0 else '')}\n"
    )
    if act.get("speaker"):
        text += f"🎙️ {act['speaker']}\n"
    if act.get("description"):
        text += f"\n_{act['description']}_\n"
    if act.get("livestream_url"):
        text += f"\n🔴 [Regarder en direct]({act['livestream_url']})\n"

    buttons = []
    if registered:
        buttons.append([InlineKeyboardButton("✅ Déjà inscrit(e)", callback_data=f"act_detail_{activity_id}")])
        buttons.append([InlineKeyboardButton("❌ Se désinscrire", callback_data=f"act_unregister_{activity_id}")])
    elif spots_left > 0:
        buttons.append([InlineKeyboardButton("✅ S'inscrire", callback_data=f"act_register_{activity_id}")])
    else:
        buttons.append([InlineKeyboardButton("📋 Liste d'attente", callback_data=f"act_waitlist_{activity_id}")])

    buttons.append([InlineKeyboardButton("🔙 Retour", callback_data="menu_activities")])
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
    )


async def cb_register_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity_id = int(query.data.split("_")[-1])
    user = update.effective_user
    result = await register_to_activity(user.id, activity_id)
    act = await get_activity(activity_id)
    title = act["title"] if act else "l'activité"
    messages = {
        "success":          f"✅ *Inscription confirmée !*\n\nVous êtes inscrit(e) à :\n*{title}*\n\nUn rappel vous sera envoyé la veille. 🔔",
        "already_registered": f"ℹ️ Vous êtes déjà inscrit(e) à *{title}*.",
        "waitlisted":       f"📋 *Liste d'attente*\n\nVous avez été ajouté(e) à la liste d'attente pour *{title}*.\nVous serez notifié(e) si une place se libère.",
        "error_no_member":  "❌ Profil introuvable. Tapez /start pour vous enregistrer.",
        "error_not_found":  "❌ Activité introuvable.",
    }
    text = messages.get(result, "❌ Une erreur est survenue.")
    keyboard = [
        [InlineKeyboardButton("📖 Mes inscriptions", callback_data="menu_my_courses")],
        [InlineKeyboardButton("🔙 Activités", callback_data="menu_activities")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def cb_unregister_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity_id = int(query.data.split("_")[-1])
    user = update.effective_user
    result = await unregister_from_activity(user.id, activity_id)
    act = await get_activity(activity_id)
    title = act["title"] if act else "l'activité"
    messages = {
        "success":         f"✅ Vous avez été désinscrit(e) de :\n*{title}*",
        "not_registered":  f"ℹ️ Vous n'étiez pas inscrit(e) à *{title}*.",
        "error_no_member": "❌ Profil introuvable. Tapez /start pour vous enregistrer.",
    }
    text = messages.get(result, "❌ Une erreur est survenue.")
    keyboard = [
        [InlineKeyboardButton("📖 Mes inscriptions", callback_data="menu_my_courses")],
        [InlineKeyboardButton("📅 Voir les activités", callback_data="menu_activities")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def cb_my_courses(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    registrations = await get_member_registrations(user.id)

    if not registrations:
        text = (
            "📖 *Mes inscriptions*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Vous n'êtes inscrit(e) à aucune activité.\n\n"
            "Découvrez les activités disponibles ! 👇"
        )
        keyboard = [
            [InlineKeyboardButton("📅 Voir les activités", callback_data="menu_activities")],
            [InlineKeyboardButton("🔙 Menu", callback_data="menu_main")],
        ]
    else:
        lines = ["📖 *Mes inscriptions*", "━━━━━━━━━━━━━━━━━━"]
        keyboard = []
        for reg in registrations:
            emoji = ACTIVITY_TYPE_EMOJI.get(reg.get("type", "autre"), "🌟")
            lines.append(
                f"\n{emoji} *{reg['title']}*\n"
                f"   📅 {reg['date']} à {reg['time']}\n"
                f"   📍 {reg.get('location', 'Mosquée')}"
            )
            keyboard.append([InlineKeyboardButton(
                f"❌ Désinscrire — {reg['title'][:30]}",
                callback_data=f"act_unregister_{reg['activity_id']}",
            )])
        keyboard.append([InlineKeyboardButton("📅 Voir plus d'activités", callback_data="menu_activities")])
        keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_main")])
        text = "\n".join(lines)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
