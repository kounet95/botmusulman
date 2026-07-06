from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import get_donation_campaigns
from services.mosque_context import resolve_user_mosque

NO_MOSQUE_TEXT = "❌ Vous n'êtes rattaché(e) à aucune mosquée. Tapez /start pour en choisir une."


def _progress_bar(current: float, goal: float, length: int = 12) -> str:
    pct = min(current / goal, 1.0) if goal else 0
    filled = int(pct * length)
    return "█" * filled + "░" * (length - filled) + f" {int(pct * 100)}%"


async def cb_donations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await query.edit_message_text(NO_MOSQUE_TEXT)
        return
    campaigns = await get_donation_campaigns(mosque["id"])
    text, markup = _build_donations_view(campaigns)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)


async def cmd_dons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mosque = await resolve_user_mosque(update.effective_user.id)
    if not mosque:
        await update.message.reply_text(NO_MOSQUE_TEXT)
        return
    campaigns = await get_donation_campaigns(mosque["id"])
    text, markup = _build_donations_view(campaigns)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)


def _build_donations_view(campaigns: list[dict]):
    lines = ["🤲 *Dons & Sadaqa*", "━━━━━━━━━━━━━━━━━━"]
    buttons = []
    if not campaigns:
        lines.append("\nAucune collecte en cours pour le moment.")
        lines.append("\n_Que Allah récompense vos dons_ 🌙")
    else:
        for camp in campaigns:
            goal = camp.get("goal_amount", 0)
            collected = camp.get("collected_amount", 0)
            bar = _progress_bar(collected, goal) if goal else ""
            lines.append(
                f"\n{'💚' if camp.get('type') == 'general' else '💛'} *{camp['title']}*\n"
                f"   {bar}\n"
                f"   Collecté : *{collected:,.0f}$* / Objectif : {goal:,.0f}$"
            )
            if camp.get("payment_url"):
                buttons.append([InlineKeyboardButton(
                    f"💳 Donner — {camp['title'][:30]}",
                    url=camp["payment_url"]
                )])
    lines.append("\n━━━━━━━━━━━━━━━━━━")
    lines.append("_Que Allah accepte vos dons et vous en récompense_ 🤲")
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_main")])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)
