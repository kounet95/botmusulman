from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.database import (
    list_distinct_cities,
    list_distinct_neighborhoods,
    list_mosques_by_location,
    get_mosque,
    get_donation_campaigns,
    upsert_member,
)
from services.prayer_api import get_prayer_times, format_prayer_times
from handlers.donations import _build_donations_view

INSTALLATION_LABELS = {
    "mosque": "🕌 Mosquée",
    "ecole": "📖 École coranique",
    "salle_priere": "🙏 Salle de prière",
    "domicile": "🏠 Domicile",
    "magasin": "🏪 Magasin",
}

AMENITY_LABELS = {
    "women_space": "Espace pour femmes",
    "ablution_room": "Salle d'ablutions",
    "adult_courses": "Cours pour adultes",
    "kids_courses": "Cours pour enfants",
    "disabled_access": "Accès handicapés",
    "library": "Bibliothèque",
    "braille_quran": "Coran pour les malvoyants",
    "janaza_prayer": "Salât al-Janaza",
    "eid_prayer": "Salat Al-Aïd",
    "ramadan_iftar": "Iftar Ramadan",
    "parking": "Parking",
    "bike_parking": "Stationnement vélo",
    "ev_charging": "Recharge de voiture électrique",
}


async def _show_cities(message_edit, context: ContextTypes.DEFAULT_TYPE):
    cities = await list_distinct_cities()
    if not cities:
        await message_edit(
            "❌ Aucun lieu n'est encore enregistré.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_main")]]),
        )
        return
    context.user_data["discover_cities"] = cities
    buttons = [
        [InlineKeyboardButton(f"📍 {city}", callback_data=f"discover_city_{i}")]
        for i, city in enumerate(cities)
    ]
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_main")])
    await message_edit(
        "🔍 *Trouver un lieu près de vous*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Choisissez une ville :",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cmd_trouver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_cities(update.message.reply_text, context)


async def cb_discover_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _show_cities(query.edit_message_text, context)


async def _show_neighborhoods(query, context: ContextTypes.DEFAULT_TYPE, city: str):
    hoods = await list_distinct_neighborhoods(city)
    if not hoods:
        # Pas de quartiers renseignés pour cette ville : on liste directement les lieux
        await _show_places(query, context, city, None)
        return
    context.user_data["discover_hoods"] = hoods
    buttons = [
        [InlineKeyboardButton(f"🧭 {hood}", callback_data=f"discover_hood_{i}")]
        for i, hood in enumerate(hoods)
    ]
    buttons.append([InlineKeyboardButton("🗺️ Tous les quartiers", callback_data="discover_hood_all")])
    buttons.append([InlineKeyboardButton("🔙 Retour aux villes", callback_data="discover_back_cities")])
    await query.edit_message_text(
        f"📍 *{city}*\n━━━━━━━━━━━━━━━━━━\nChoisissez un quartier :",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cb_discover_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[-1])
    cities = context.user_data.get("discover_cities", [])
    if idx >= len(cities):
        await query.edit_message_text("❌ Session expirée, tapez /trouver pour recommencer.")
        return
    city = cities[idx]
    context.user_data["discover_city"] = city
    await _show_neighborhoods(query, context, city)


async def _show_places(query, context: ContextTypes.DEFAULT_TYPE, city: str, neighborhood: str | None):
    places = await list_mosques_by_location(city, neighborhood)
    label = f"{city}, {neighborhood}" if neighborhood else city
    if not places:
        buttons = [[InlineKeyboardButton("🔙 Retour", callback_data="discover_back_hoods")]]
        await query.edit_message_text(
            f"❌ Aucun lieu trouvé à *{label}*.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return
    buttons = [
        [InlineKeyboardButton(
            f"{INSTALLATION_LABELS.get(p.get('installation_type'), '📍')} {p['name']}",
            callback_data=f"discover_view_{p['id']}",
        )]
        for p in places
    ]
    buttons.append([InlineKeyboardButton("🔙 Retour", callback_data="discover_back_hoods")])
    await query.edit_message_text(
        f"📍 *{label}*\n━━━━━━━━━━━━━━━━━━\n{len(places)} lieu(x) trouvé(s) :",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cb_discover_hood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = context.user_data.get("discover_city")
    if not city:
        await query.edit_message_text("❌ Session expirée, tapez /trouver pour recommencer.")
        return
    suffix = query.data.split("_")[-1]
    if suffix == "all":
        await _show_places(query, context, city, None)
        return
    hoods = context.user_data.get("discover_hoods", [])
    idx = int(suffix)
    if idx >= len(hoods):
        await query.edit_message_text("❌ Session expirée, tapez /trouver pour recommencer.")
        return
    await _show_places(query, context, city, hoods[idx])


async def cb_discover_back_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _show_cities(query.edit_message_text, context)


async def cb_discover_back_hoods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = context.user_data.get("discover_city")
    if not city:
        await _show_cities(query.edit_message_text, context)
        return
    await _show_neighborhoods(query, context, city)


def _place_detail_text(place: dict) -> str:
    type_label = INSTALLATION_LABELS.get(place.get("installation_type"), "📍 Lieu")
    lines = [f"{type_label} *{place['name']}*", "━━━━━━━━━━━━━━━━━━"]

    location = place["city"]
    if place.get("neighborhood"):
        location += f", {place['neighborhood']}"
    lines.append(f"📍 {place.get('address') or ''} — {location}".strip(" —"))

    if place.get("association_name"):
        lines.append(f"🏷️ {place['association_name']}")
    if place.get("phone"):
        lines.append(f"📞 {place['phone']}")
    if place.get("email"):
        lines.append(f"📧 {place['email']}")
    if place.get("website"):
        lines.append(f"🌐 {place['website']}")

    amenities = [AMENITY_LABELS[k] for k in (place.get("amenities") or []) if k in AMENITY_LABELS]
    if amenities:
        lines.append("\n✨ *Installations & services*")
        lines.append(", ".join(amenities))

    if place.get("capacity_men") or place.get("capacity_women"):
        cap = []
        if place.get("capacity_men"):
            cap.append(f"{place['capacity_men']} hommes")
        if place.get("capacity_women"):
            cap.append(f"{place['capacity_women']} femmes")
        lines.append(f"\n👥 Capacité : {', '.join(cap)}")

    if place.get("history"):
        lines.append(f"\n📖 _{place['history']}_")
    if place.get("other_info"):
        lines.append(f"\nℹ️ {place['other_info']}")

    return "\n".join(lines)


async def cb_discover_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque_id = int(query.data.split("_")[-1])
    place = await get_mosque(mosque_id)
    if not place:
        await query.edit_message_text("❌ Lieu introuvable.")
        return

    context.user_data["discover_last_view"] = mosque_id
    buttons = [
        [InlineKeyboardButton("🕐 Horaires de prière", callback_data=f"discover_prayer_{mosque_id}")],
        [InlineKeyboardButton("🤲 Faire un don", callback_data=f"discover_donate_{mosque_id}")],
        [InlineKeyboardButton("✅ En faire mon lieu de culte", callback_data=f"discover_setmine_{mosque_id}")],
        [InlineKeyboardButton("🔙 Retour à la liste", callback_data="discover_back_hoods")],
    ]
    await query.edit_message_text(
        _place_detail_text(place),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cb_discover_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque_id = int(query.data.split("_")[-1])
    place = await get_mosque(mosque_id)
    if not place:
        await query.edit_message_text("❌ Lieu introuvable.")
        return

    timings = await get_prayer_times(place["city"], place["country"])
    label = f"{place['city']}, {place['neighborhood']}" if place.get("neighborhood") else place["city"]
    text = format_prayer_times(timings, label) if timings else "❌ Impossible de récupérer les horaires."
    buttons = [[InlineKeyboardButton("🔙 Retour", callback_data=f"discover_view_{mosque_id}")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def cb_discover_donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque_id = int(query.data.split("_")[-1])
    place = await get_mosque(mosque_id)
    if not place:
        await query.edit_message_text("❌ Lieu introuvable.")
        return

    campaigns = await get_donation_campaigns(mosque_id)
    text, markup = _build_donations_view(campaigns, place["name"], back_callback=f"discover_view_{mosque_id}")
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)


async def cb_discover_setmine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque_id = int(query.data.split("_")[-1])
    place = await get_mosque(mosque_id)
    if not place:
        await query.edit_message_text("❌ Lieu introuvable.")
        return

    user = update.effective_user
    await upsert_member(user.id, user.first_name, user.username, mosque_id)
    buttons = [[InlineKeyboardButton("🔙 Menu", callback_data="menu_main")]]
    await query.edit_message_text(
        f"✅ *{place['name']}* est maintenant votre lieu de culte.\n\n"
        "Vous recevrez ses horaires de prière, annonces et activités 🤲",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
