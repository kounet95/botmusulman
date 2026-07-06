from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta
import pytz
import logging

from services.prayer_api import get_prayer_times
from services.weather_api import get_weather_alert
from services.database import (
    get_members_with_pref, get_upcoming_activities,
    get_activities_on_date, get_registered_members_for_activity,
    list_mosques,
)

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler(timezone=pytz.timezone("Africa/Conakry"))
_app = None  # telegram Application reference

# Évite de renvoyer la même alerte météo plusieurs fois le même jour (mosque_id -> date)
_last_weather_alert_date: dict[int, date] = {}

# ── Dates clés Dhul Hijja 1447 AH (2026) ────────────────────────────────────
# À mettre à jour chaque année (convertir depuis un calendrier hégirien)
DHUL_HIJJA_START = date(2026, 5, 28)   # 1er Dhul Hijja 1447
YAWM_ARAFAH      = date(2026, 6,  5)   # 9 Dhul Hijja — jeûne recommandé
EID_AL_ADHA      = date(2026, 6,  6)   # 10 Dhul Hijja — Aïd el-Adha

# ── Tips Hajj/Omra (rotation hebdomadaire) ──────────────────────────────────
_HAJJ_UMRAH_TIPS = [
    (
        "🕋 *Hajj & Omra — Le 5ème pilier*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Le Hajj est obligatoire une fois dans la vie pour tout musulman "
        "qui en a la capacité physique et financière.\n\n"
        "_« Et c'est un devoir envers Allah pour les gens qui peuvent s'y rendre »_\n"
        "— Sourate Al-Imran (3:97)\n\n"
        "Commencez dès aujourd'hui à épargner pour ce voyage béni 🤲"
    ),
    (
        "🕋 *Les vertus de l'Omra*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Le Prophète ﷺ a dit :\n"
        "_« Une Omra jusqu'à la prochaine est une expiation pour les péchés commis entre les deux. »_\n"
        "— Bukhari & Muslim\n\n"
        "L'Omra peut se faire à tout moment de l'année — consultez votre mosquée "
        "pour les voyages de groupe ! 🤲"
    ),
    (
        "🕋 *Préparation spirituelle*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Avant le Hajj ou l'Omra :\n"
        "• Sincère Tawbah (repentir)\n"
        "• Rembourser ses dettes\n"
        "• Demander pardon à ceux qu'on a lésés\n"
        "• Apprendre les rites (Manasik)\n"
        "• Constituer une épargne Halal\n\n"
        "_Le Hajj mabrour n'a comme récompense que le Paradis._\n"
        "— Bukhari & Muslim 🤲"
    ),
    (
        "🕋 *Les étapes de l'Omra*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ *Ihram* — Intention sacrée depuis le Miqat\n"
        "2️⃣ *Tawaf* — 7 tours autour de la Ka'bah\n"
        "3️⃣ *Sa'y* — 7 allers-retours entre Safa et Marwa\n"
        "4️⃣ *Tahallul* — Coupe des cheveux (sortie de l'Ihram)\n\n"
        "_Et accomplis le Hajj et l'Omra pour Allah._\n"
        "— Sourate Al-Baqarah (2:196) 🤲"
    ),
    (
        "🕋 *Les 10 jours de Dhul Hijja*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Le Prophète ﷺ a dit :\n"
        "_« Il n'y a pas de jours où les bonnes œuvres sont plus aimées d'Allah que ces dix jours. »_\n"
        "— Bukhari\n\n"
        "Pendant ces jours bénis :\n"
        "• Faites beaucoup de Dhikr (Takbir, Tahmid, Tahlil)\n"
        "• Jeûnez les 9 premiers jours si possible\n"
        "• Donnez en Sadaqa\n"
        "• Récitez le Coran abondamment 🤲"
    ),
    (
        "🕋 *Le jour d'Arafah — le plus béni*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Le Prophète ﷺ a dit :\n"
        "_« Le jeûne du jour d'Arafah efface les péchés de l'année précédente "
        "et de l'année suivante. »_\n"
        "— Muslim\n\n"
        "Le jour d'Arafah est le 9 Dhul Hijja.\n"
        "C'est le jour le plus béni de l'année pour ceux qui ne font pas le Hajj ! 🤲"
    ),
    (
        "🕋 *Organiser son Hajj*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Pour préparer votre Hajj :\n"
        "• Contactez une agence de voyage agréée\n"
        "• Renseignez-vous auprès de la mosquée (groupes organisés)\n"
        "• Faites votre demande de visa tôt (quotas limités)\n"
        "• Préparez les vaccins obligatoires (méningite, COVID...)\n"
        "• Apprenez les rites avec un guide certifié\n\n"
        "Que Allah vous facilite ce voyage béni 🤲"
    ),
    (
        "🕋 *Dua du Tawaf*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّار\n\n"
        "_« Notre Seigneur, accorde-nous une belle part en ce monde et une belle part "
        "dans l'Au-delà, et préserve-nous du châtiment du Feu. »_\n"
        "— Sourate Al-Baqarah (2:201)\n\n"
        "Apprenez cette dua et répétez-la souvent 🤲"
    ),
]


# ── Init ─────────────────────────────────────────────────────────────────────

def init_scheduler(app):
    global _app
    _app = app

    # Horaires de prière — chaque matin à 5h30
    _scheduler.add_job(send_daily_prayer_times, CronTrigger(hour=5, minute=30))

    # Rappel Jumu'a — vendredi 9h et 11h30
    _scheduler.add_job(send_jumua_reminder, CronTrigger(day_of_week="fri", hour=9,  minute=0))
    _scheduler.add_job(send_jumua_reminder, CronTrigger(day_of_week="fri", hour=11, minute=30))

    # Hadith du jour — 6h
    _scheduler.add_job(send_daily_hadith, CronTrigger(hour=6, minute=0))

    # Rappels activités — chaque matin à 8h
    _scheduler.add_job(send_activity_reminders, CronTrigger(hour=8, minute=0))

    # Hajj & Omra — tip hebdomadaire chaque dimanche à 9h
    _scheduler.add_job(send_hajj_umrah_weekly_tip, CronTrigger(day_of_week="sun", hour=9, minute=0))

    # Rappels spéciaux islamiques — vérification quotidienne à 7h
    _scheduler.add_job(send_special_islamic_reminders, CronTrigger(hour=7, minute=0))

    # Alerte météo (orage, fortes pluies, vents violents) — 6h et 14h
    _scheduler.add_job(send_weather_alerts, CronTrigger(hour="6,14", minute=0))

    _scheduler.start()
    logger.info("Scheduler démarré")


# ── Broadcast helper ─────────────────────────────────────────────────────────

async def _broadcast(members: list[dict], text: str, parse_mode: str = "Markdown"):
    if not _app:
        return
    for m in members:
        try:
            await _app.bot.send_message(
                chat_id=m["telegram_id"],
                text=text,
                parse_mode=parse_mode,
            )
        except Exception as e:
            logger.warning(f"Impossible d'envoyer à {m['telegram_id']}: {e}")


# ── Jobs ─────────────────────────────────────────────────────────────────────

async def send_daily_prayer_times():
    from services.prayer_api import format_prayer_times
    for mosque in await list_mosques():
        timings = await get_prayer_times(mosque["city"], mosque["country"])
        if not timings:
            continue
        text = format_prayer_times(timings, mosque["city"])
        members = await get_members_with_pref(mosque["id"], "prayer_times")
        await _broadcast(members, text)


async def send_jumua_reminder():
    text = (
        "🕌 *Rappel — Prière du Vendredi (Jumu'a)*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "N'oubliez pas la prière du Vendredi aujourd'hui !\n\n"
        "_« O vous qui croyez ! Quand on appelle à la prière du vendredi, "
        "empressez-vous au rappel d'Allah »_\n"
        "— Sourate Al-Jumu'a (62:9)\n\n"
        "Que Allah accepte vos prières 🤲"
    )
    for mosque in await list_mosques():
        members = await get_members_with_pref(mosque["id"], "jumua")
        await _broadcast(members, text)


async def send_daily_hadith():
    from services.database import get_daily_content
    type_labels = {"hadith": "📖 Hadith du jour", "verset": "✨ Verset du jour", "rappel": "💡 Rappel du jour", "dua": "🤲 Dua du jour"}
    for mosque in await list_mosques():
        content = await get_daily_content("hadith", mosque["id"])
        if not content:
            content = await get_daily_content("verset", mosque["id"])
        if not content:
            content = await get_daily_content("rappel", mosque["id"])
        if not content:
            continue
        title = type_labels.get(content.get("type", "hadith"), "📖 Du jour")
        text = (
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{content.get('content_fr', '')}\n\n"
            f"_{content.get('source', '')}_"
        )
        members = await get_members_with_pref(mosque["id"], "announcements")
        await _broadcast(members, text)


async def send_activity_reminders():
    """Envoie des rappels aux membres inscrits : J-3, J-1 et jour-J."""
    from handlers.activities import ACTIVITY_TYPE_EMOJI

    today = date.today()

    windows = [
        (3, "📅 *Rappel — Dans 3 jours*",   "Préparez-vous et invitez un proche ! 🤝"),
        (1, "⏰ *Rappel — C'est demain !*",  "N'oubliez pas de noter l'heure et le lieu. 📍"),
        (0, "🔔 *Rappel — C'est aujourd'hui !*", "Nous vous attendons à la mosquée. 🕌"),
    ]

    mosques = await list_mosques()
    for days_ahead, header, footer in windows:
        target_date = today + timedelta(days=days_ahead)

        for mosque in mosques:
            activities = await get_activities_on_date(mosque["id"], target_date)

            for act in activities:
                members = await get_registered_members_for_activity(act["id"])
                if not members:
                    continue

                emoji = ACTIVITY_TYPE_EMOJI.get(act.get("type", "autre"), "🌟")
                price_str = "Gratuit 🎁" if not act.get("is_paid") else f"{act.get('price', '?')}$ 💳"

                text = (
                    f"{header}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{emoji} *{act['title']}*\n"
                    f"🕐 {act['time']}  |  📍 {act.get('location', 'Mosquée')}\n"
                    f"💰 {price_str}\n"
                )
                if act.get("speaker"):
                    text += f"🎙️ {act['speaker']}\n"
                text += f"\n_{footer}_"

                await _broadcast(members, text)
                logger.info(
                    f"Rappel J-{days_ahead} envoyé pour « {act['title']} » "
                    f"({len(members)} inscrits)"
                )


async def send_hajj_umrah_weekly_tip():
    """Tip Hajj/Omra hebdomadaire, rotation sur 8 semaines."""
    from datetime import datetime
    week = datetime.now().isocalendar()[1]
    tip = _HAJJ_UMRAH_TIPS[week % len(_HAJJ_UMRAH_TIPS)]
    for mosque in await list_mosques():
        members = await get_members_with_pref(mosque["id"], "hajj_umrah")
        await _broadcast(members, tip)
        logger.info(f"Tip Hajj/Omra semaine {week} envoyé à {len(members)} membres de {mosque['name']}")


async def send_special_islamic_reminders():
    """Rappels liés aux dates clés du calendrier hégirien."""
    today = date.today()
    mosques = await list_mosques()

    # ── 10 jours de Dhul Hijja (1er au 9) ──────────────────────────────────
    if DHUL_HIJJA_START <= today < YAWM_ARAFAH:
        day_num = (today - DHUL_HIJJA_START).days + 1
        text = (
            f"✨ *{day_num}{'er' if day_num == 1 else 'ème'} jour de Dhul Hijja*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Nous sommes dans les jours les plus bénis de l'année !\n\n"
            "Profitez-en pour :\n"
            "• Dire *Allahu Akbar, Alhamdulillah, La ilaha illa Allah*\n"
            "• Jeûner (surtout le 9ème jour — Arafah)\n"
            "• Donner en Sadaqa\n"
            "• Réciter le Coran\n\n"
            "_« Il n'y a pas de jours où les bonnes œuvres sont plus aimées d'Allah »_\n"
            "— Bukhari 🤲"
        )
        for mosque in mosques:
            members = await get_members_with_pref(mosque["id"], "hajj_umrah")
            await _broadcast(members, text)
        logger.info(f"Rappel Dhul Hijja jour {day_num} envoyé")

    # ── Jour d'Arafah ────────────────────────────────────────────────────────
    elif today == YAWM_ARAFAH:
        text = (
            "🌟 *YAWM ARAFAH — Jour le plus béni de l'année !*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Le Prophète ﷺ a dit :\n"
            "_« Le jeûne du jour d'Arafah efface les péchés de l'année précédente "
            "et de l'année suivante. »_\n"
            "— Muslim\n\n"
            "Que faire aujourd'hui :\n"
            "🌙 Jeûner (pour ceux qui ne font pas le Hajj)\n"
            "📿 Faire beaucoup de Dhikr et de Dua\n"
            "📖 Réciter Sourate Al-Ikhlas, Al-Falaq, An-Nas\n"
            "🤲 Dua : *اللَّهُمَّ إِنَّكَ عَفُوٌّ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي*\n\n"
            "Qu'Allah accepte nos actes et nous pardonne 🤲"
        )
        # Envoyé à tous (annonces) + Hajj, par mosquée
        for mosque in mosques:
            members_hajj = await get_members_with_pref(mosque["id"], "hajj_umrah")
            members_ann  = await get_members_with_pref(mosque["id"], "announcements")
            # Fusionner sans doublons
            seen = set()
            all_members = []
            for m in members_hajj + members_ann:
                if m["telegram_id"] not in seen:
                    seen.add(m["telegram_id"])
                    all_members.append(m)
            await _broadcast(all_members, text)
        logger.info("Rappel Yawm Arafah envoyé")

    # ── Aïd el-Adha ─────────────────────────────────────────────────────────
    elif today == EID_AL_ADHA:
        text = (
            "🎉 *Aïd Moubarak ! عيد مبارك*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Toute l'équipe de la mosquée vous souhaite\n"
            "un *Aïd el-Adha* béni et rempli de joie !\n\n"
            "N'oubliez pas :\n"
            "🕌 La prière de l'Aïd ce matin\n"
            "🐑 Le sacrifice (Udhiya) si vous en avez la capacité\n"
            "🤝 Partager avec les voisins et les nécessiteux\n\n"
            "_Taqabbal Allahu minna wa minkum_ 🤲\n"
            "Qu'Allah accepte nos actes d'adoration !"
        )
        for mosque in mosques:
            members = await get_members_with_pref(mosque["id"], "announcements")
            await _broadcast(members, text)
        logger.info("Message Aïd el-Adha envoyé")

    # ── Rappel 30 jours avant Dhul Hijja ────────────────────────────────────
    elif today == DHUL_HIJJA_START - timedelta(days=30):
        text = (
            "🕋 *Dans 30 jours — Dhul Hijja approche !*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Dans un mois commencent les 10 jours les plus bénis de l'année.\n\n"
            "Préparez-vous dès maintenant :\n"
            "• Intensifiez vos actes d'adoration\n"
            "• Planifiez votre Omra ou votre Hajj\n"
            "• Contactez la mosquée pour les groupes de voyage\n\n"
            "Que Allah nous permette de vivre ces jours bénis 🤲"
        )
        for mosque in mosques:
            members = await get_members_with_pref(mosque["id"], "hajj_umrah")
            await _broadcast(members, text)
        logger.info("Rappel J-30 Dhul Hijja envoyé")


async def send_weather_alerts():
    """Vérifie la météo des prochaines 24h pour chaque mosquée et alerte les
    membres en cas d'orage, de fortes pluies ou de vents violents à venir."""
    today = date.today()
    for mosque in await list_mosques():
        alert = await get_weather_alert(mosque["city"], mosque["country"])
        if not alert:
            continue
        if _last_weather_alert_date.get(mosque["id"]) == today:
            continue  # déjà envoyée aujourd'hui

        text = (
            f"⚠️ *Alerte météo — {mosque['city']}*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{alert['message']} vers {alert['expected_time']}.\n\n"
            "Prenez vos précautions pour vos déplacements à la mosquée 🤲"
        )
        members = await get_members_with_pref(mosque["id"], "announcements")
        await _broadcast(members, text)
        _last_weather_alert_date[mosque["id"]] = today
        logger.info(f"Alerte météo envoyée pour {mosque['name']}: {alert['message']}")
