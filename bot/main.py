import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN
from handlers.start import cmd_start, cmd_menu, cb_about, cb_pick_mosque
from handlers.prayer_times import cmd_prieres, cb_prayer, cmd_prochaine
from handlers.activities import (
    cmd_activites, cb_activities, cb_activity_detail,
    cb_register_activity, cb_unregister_activity, cb_my_courses,
)
from handlers.notifications import cb_notifications, cb_toggle_notif
from handlers.donations import cmd_dons, cb_donations
from services.scheduler import init_scheduler

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
    keyboard = [
        [
            InlineKeyboardButton("🕌 Horaires de prière", callback_data="menu_prayer"),
            InlineKeyboardButton("📅 Activités", callback_data="menu_activities"),
        ],
        [
            InlineKeyboardButton("📖 Mes inscriptions", callback_data="menu_my_courses"),
            InlineKeyboardButton("🤲 Dons", callback_data="menu_donations"),
        ],
        [
            InlineKeyboardButton("🔔 Mes notifications", callback_data="menu_notifications"),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("*Menu principal* 🌙", parse_mode="Markdown", reply_markup=markup)


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("prieres", cmd_prieres))
    app.add_handler(CommandHandler("prochaine", cmd_prochaine))
    app.add_handler(CommandHandler("activites", cmd_activites))
    app.add_handler(CommandHandler("dons", cmd_dons))

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

    # Callback — activities
    app.add_handler(CallbackQueryHandler(cb_activity_detail, pattern=r"^act_detail_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_register_activity, pattern=r"^act_register_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_register_activity, pattern=r"^act_waitlist_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_unregister_activity, pattern=r"^act_unregister_\d+$"))

    # Callback — notifications
    app.add_handler(CallbackQueryHandler(cb_toggle_notif, pattern=r"^notif_toggle_.+$"))

    # Scheduler
    init_scheduler(app)

    logger.info("Bot démarré")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
