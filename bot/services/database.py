import asyncpg
from config import DATABASE_URL

_pool = None

async def get_db():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool


# ── Mosquées ─────────────────────────────────────────────────────────────────

async def get_mosque(mosque_id: int) -> dict | None:
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM mosques WHERE id = $1", mosque_id)
        return dict(row) if row else None


async def get_mosque_by_slug(slug: str) -> dict | None:
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM mosques WHERE slug = $1", slug)
        return dict(row) if row else None


async def list_mosques() -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM mosques ORDER BY name")
        return [dict(row) for row in rows]


# ── Members ──────────────────────────────────────────────────────────────────

async def upsert_member(telegram_id: int, first_name: str, username: str | None, mosque_id: int):
    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO members (telegram_id, first_name, username, mosque_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                username = EXCLUDED.username,
                mosque_id = EXCLUDED.mosque_id
        """, str(telegram_id), first_name, username or "", mosque_id)


async def get_member(telegram_id: int) -> dict | None:
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM members WHERE telegram_id = $1", str(telegram_id))
        return dict(row) if row else None


_DEFAULT_PREFS = {
    "prayer_times": True,
    "jumua":        True,
    "courses":      True,
    "conferences":  True,
    "announcements": True,
    "hajj_umrah":   True,
}


async def get_member_prefs(telegram_id: int) -> dict:
    member = await get_member(telegram_id)
    if not member:
        return dict(_DEFAULT_PREFS)
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM notification_preferences WHERE member_id = $1", member["id"])
        if row:
            prefs = dict(_DEFAULT_PREFS)
            prefs.update({k: v for k, v in dict(row).items() if v is not None})
            return prefs
        return dict(_DEFAULT_PREFS)


async def update_member_pref(telegram_id: int, pref_key: str, value: bool):
    member = await get_member(telegram_id)
    if not member:
        return
    pool = await get_db()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM notification_preferences WHERE member_id = $1", member["id"])
        if existing:
            await conn.execute(f"UPDATE notification_preferences SET {pref_key} = $1 WHERE member_id = $2", value, member["id"])
        else:
            await conn.execute(f"INSERT INTO notification_preferences (member_id, {pref_key}) VALUES ($1, $2)", member["id"], value)


# ── Activities ────────────────────────────────────────────────────────────────

async def get_upcoming_activities(mosque_id: int, type_filter: str | None = None) -> list[dict]:
    from datetime import datetime
    pool = await get_db()
    async with pool.acquire() as conn:
        today = datetime.now().date()
        if type_filter:
            rows = await conn.fetch(
                "SELECT * FROM activities WHERE mosque_id = $1 AND date >= $2 AND type = $3 ORDER BY date LIMIT 10",
                mosque_id, today, type_filter,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM activities WHERE mosque_id = $1 AND date >= $2 ORDER BY date LIMIT 10",
                mosque_id, today,
            )
        return [dict(row) for row in rows]


async def get_activity(activity_id: int) -> dict | None:
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM activities WHERE id = $1", activity_id)
        return dict(row) if row else None


async def is_member_registered(telegram_id: int, activity_id: int) -> bool:
    pool = await get_db()
    async with pool.acquire() as conn:
        member = await get_member(telegram_id)
        if not member:
            return False
        row = await conn.fetchrow(
            "SELECT id FROM registrations WHERE member_id = $1 AND activity_id = $2",
            member["id"], activity_id,
        )
        return row is not None


async def register_to_activity(telegram_id: int, activity_id: int) -> str:
    pool = await get_db()
    async with pool.acquire() as conn:
        async with conn.transaction():
            member = await get_member(telegram_id)
            if not member:
                return "error_no_member"
            activity = await get_activity(activity_id)
            if not activity or activity["mosque_id"] != member["mosque_id"]:
                return "error_not_found"
            existing = await conn.fetchrow("SELECT id FROM registrations WHERE member_id = $1 AND activity_id = $2", member["id"], activity_id)
            if existing:
                return "already_registered"
            if activity["registered_count"] >= activity["capacity"]:
                await conn.execute("INSERT INTO waitlist (member_id, activity_id) VALUES ($1, $2)", member["id"], activity_id)
                return "waitlisted"
            await conn.execute("INSERT INTO registrations (member_id, activity_id) VALUES ($1, $2)", member["id"], activity_id)
            await conn.execute("UPDATE activities SET registered_count = registered_count + 1 WHERE id = $1", activity_id)
            return "success"


async def unregister_from_activity(telegram_id: int, activity_id: int) -> str:
    pool = await get_db()
    async with pool.acquire() as conn:
        async with conn.transaction():
            member = await get_member(telegram_id)
            if not member:
                return "error_no_member"
            existing = await conn.fetchrow(
                "SELECT id FROM registrations WHERE member_id = $1 AND activity_id = $2",
                member["id"], activity_id,
            )
            if not existing:
                return "not_registered"
            await conn.execute(
                "DELETE FROM registrations WHERE member_id = $1 AND activity_id = $2",
                member["id"], activity_id,
            )
            await conn.execute(
                "UPDATE activities SET registered_count = GREATEST(registered_count - 1, 0) WHERE id = $1",
                activity_id,
            )
            return "success"


async def get_member_registrations(telegram_id: int) -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        member = await get_member(telegram_id)
        if not member:
            return []
        rows = await conn.fetch("""
            SELECT
                r.id          AS reg_id,
                r.registered_at,
                a.id          AS activity_id,
                a.title,
                a.type,
                a.date,
                a.time,
                a.location,
                a.speaker,
                a.registered_count,
                a.capacity
            FROM registrations r
            JOIN activities a ON r.activity_id = a.id
            WHERE r.member_id = $1
            ORDER BY a.date ASC
        """, member["id"])
        return [dict(row) for row in rows]


# ── Content ───────────────────────────────────────────────────────────────────

async def get_daily_content(content_type: str, mosque_id: int) -> dict | None:
    from datetime import datetime
    pool = await get_db()
    async with pool.acquire() as conn:
        today = datetime.now().date()
        row = await conn.fetchrow(
            "SELECT * FROM content_schedule WHERE mosque_id = $1 AND type = $2 AND scheduled_date = $3",
            mosque_id, content_type, today,
        )
        return dict(row) if row else None


# ── Donations ─────────────────────────────────────────────────────────────────

async def get_donation_campaigns(mosque_id: int) -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM donation_campaigns WHERE mosque_id = $1 AND is_active = true ORDER BY created_at DESC", mosque_id)
        return [dict(row) for row in rows]


# ── Members with prayer pref ──────────────────────────────────────────────────

async def get_members_with_pref(mosque_id: int, pref_key: str) -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT m.telegram_id, np.* FROM members m
            LEFT JOIN notification_preferences np ON m.id = np.member_id
            WHERE m.mosque_id = $1
        """, mosque_id)
        result = []
        for row in rows:
            prefs = dict(row)
            # Seule une valeur explicitement False désactive la notif
            if prefs.get(pref_key) is False:
                continue
            result.append({"telegram_id": prefs["telegram_id"], "notification_preferences": prefs})
        return result


async def get_registered_members_for_activity(activity_id: int) -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT m.telegram_id FROM registrations r
            JOIN members m ON r.member_id = m.id
            WHERE r.activity_id = $1
        """, activity_id)
        return [{"telegram_id": row["telegram_id"]} for row in rows]


async def get_activities_on_date(mosque_id: int, target_date) -> list[dict]:
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM activities WHERE mosque_id = $1 AND date = $2",
            mosque_id, target_date,
        )
        return [dict(row) for row in rows]
