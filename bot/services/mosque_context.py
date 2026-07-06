from services.database import get_member, get_mosque


async def resolve_user_mosque(telegram_id: int) -> dict | None:
    """Retourne la mosquée associée à ce membre, ou None s'il n'en a pas encore choisi une."""
    member = await get_member(telegram_id)
    if not member or not member.get("mosque_id"):
        return None
    return await get_mosque(member["mosque_id"])
