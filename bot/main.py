import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN
from handlers.start import cmd_start, cmd_menu, cb_about, cb_pick_mosque, _main_menu_markup
from handlers.prayer_times import cmd_prieres, cb_prayer, cmd_prochaine
from handlers.activities import (
    cmd_activites, cb_activities, cb_activity_detail,
    cb_register_activity, cb_unregister_activity, cb_my_courses,
)
from handlers.notifications import cb_notifications, cb_toggle_notif
from handlers.donations import cmd_dons, cb_donations
from handlers.discover import (
    cmd_trouver, cb_discover_start, cb_discover_city, cb_discover_hood,
    cb_discover_back_cities, cb_discover_back_hoods, cb_discover_view,
    cb_discover_prayer, cb_discover_donate, cb_discover_setmine,
)
from handlers.quran import (
    cmd_coran, cb_quran_start, handle_text_question, handle_voice_question,
)
from services.scheduler import init_scheduler
from services.quran_api import preload as preload_quran
from services.quran_tts import preload as preload_tts

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# httpx logue l'URL complète de chaque requête (https://api.telegram.org/bot<TOKEN>/...)
# à INFO — on la baisse à WARNING pour éviter de faire fuiter le token dans les logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def cb_menu_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "*Menu principal* 🌙", parse_mode="Markdown", reply_markup=_main_menu_markup()
    )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("prieres", cmd_prieres))
    app.add_handler(CommandHandler("prochaine", cmd_prochaine))
    app.add_handler(CommandHandler("activites", cmd_activites))
    app.add_handler(CommandHandler("dons", cmd_dons))
    app.add_handler(CommandHandler("trouver", cmd_trouver))
    app.add_handler(CommandHandler("coran", cmd_coran))

    # Callback — sélection de mosquée
    app.add_handler(CallbackQueryHandler(cb_pick_mosque, pattern=r"^pick_mosque_\d+$"))

    # Callback — menu navigation
    app.add_handler(CallbackQueryHandler(cb_menu_main, pattern="^menu_main$"))
    app.add_handler(CallbackQueryHandler(cb_prayer, pattern="^menu_prayer$"))
    # Gère menu_activities, menu_activities_cours, menu_activities_conference, etc.
    app.add_handler(CallbackQueryHandler(cb_activities, pattern=r"^menu_activities"))
    app.add_handler(CallbackQueryHandler(cb_my_courses, pattern="^menu_my_courses$"))
    app.add_handler(CallbackQueryHandler(cb_donations, pattern="^menu_donations$"))
    app.add_handler(CallbackQueryHandler(cb_notifications, pattern="^menu_notifications$"))
    app.add_handler(CallbackQueryHandler(cb_about, pattern="^menu_about$"))
    app.add_handler(CallbackQueryHandler(cb_quran_start, pattern="^menu_quran$"))

    # Callback — activities
    app.add_handler(CallbackQueryHandler(cb_activity_detail, pattern=r"^act_detail_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_register_activity, pattern=r"^act_register_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_register_activity, pattern=r"^act_waitlist_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_unregister_activity, pattern=r"^act_unregister_\d+$"))

    # Callback — notifications
    app.add_handler(CallbackQueryHandler(cb_toggle_notif, pattern=r"^notif_toggle_.+$"))

    # Callback — découverte de lieux (mosquées, salles de prière, écoles...)
    app.add_handler(CallbackQueryHandler(cb_discover_start, pattern="^menu_discover$"))
    app.add_handler(CallbackQueryHandler(cb_discover_city, pattern=r"^discover_city_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_discover_hood, pattern=r"^discover_hood_(\d+|all)$"))
    app.add_handler(CallbackQueryHandler(cb_discover_back_cities, pattern="^discover_back_cities$"))
    app.add_handler(CallbackQueryHandler(cb_discover_back_hoods, pattern="^discover_back_hoods$"))
    app.add_handler(CallbackQueryHandler(cb_discover_view, pattern=r"^discover_view_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_discover_prayer, pattern=r"^discover_prayer_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_discover_donate, pattern=r"^discover_donate_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_discover_setmine, pattern=r"^discover_setmine_\d+$"))

    # Question coranique — note vocale (toujours active) ou texte (après /coran ou le bouton menu)
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_question))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_question))

    # Scheduler
    init_scheduler(app)

    # Précharge l'index des versets coraniques (~5 Mo) pour éviter la latence
    # au premier message des utilisateurs.
    preload_quran()

    # Précharge le modèle Meta MMS-TTS (~280 Mo, téléchargé depuis HuggingFace
    # au premier démarrage) pour la réponse vocale en pular. Échoue en silence
    # si indisponible — la fonctionnalité repasse alors en texte seul.
    logger.info("Chargement du modèle TTS pular (Meta MMS)...")
    preload_tts()

    logger.info("Bot démarré")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
