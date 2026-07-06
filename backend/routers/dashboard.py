import asyncio

from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_mosque_id
from database import get_db
from datetime import datetime
from services.prayer_api import get_prayer_times, get_next_prayer
from services.weather_api import get_weather, get_weather_alert

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        members_count = await conn.fetchval("SELECT COUNT(*) FROM members WHERE mosque_id = $1", mosque_id)
        activities_count = await conn.fetchval(
            "SELECT COUNT(*) FROM activities WHERE mosque_id = $1 AND date >= $2",
            mosque_id,
            datetime.now().date().replace(day=1)
        )
        registrations_count = await conn.fetchval(
            "SELECT COUNT(*) FROM registrations r JOIN activities a ON r.activity_id = a.id WHERE a.mosque_id = $1",
            mosque_id
        )
        donations = await conn.fetch(
            "SELECT collected_amount FROM donation_campaigns WHERE mosque_id = $1 AND is_active = true",
            mosque_id
        )
        total_donations = sum(float(d['collected_amount'] or 0) for d in donations)

        return {
            "total_members": members_count or 0,
            "activities_this_month": activities_count or 0,
            "total_registrations": registrations_count or 0,
            "total_donations": total_donations,
        }


@router.get("/activities/recent")
async def recent_activities(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, title, date, time, registered_count, capacity, type
               FROM activities
               WHERE mosque_id = $1 AND date >= $2
               ORDER BY date LIMIT 5""",
            mosque_id,
            datetime.now().date()
        )
        return [dict(row) for row in rows]


@router.get("/prayer-times")
async def prayer_times(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        mosque = await conn.fetchrow("SELECT city, country FROM mosques WHERE id = $1", mosque_id)
        if not mosque:
            raise HTTPException(404, "Mosquée introuvable")

    result, weather, weather_alert = await asyncio.gather(
        get_prayer_times(mosque["city"], mosque["country"]),
        get_weather(mosque["city"], mosque["country"]),
        get_weather_alert(mosque["city"], mosque["country"]),
    )
    if not result:
        raise HTTPException(502, "Impossible de récupérer les horaires de prière")

    return {
        "timings": result["timings"],
        "sunrise": result["sunrise"],
        "next_prayer": get_next_prayer(result["timings"]),
        "gregorian_date": result["gregorian_date"],
        "hijri_date": result["hijri_date"],
        "weather": weather,
        "weather_alert": weather_alert,
    }
