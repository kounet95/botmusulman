from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_mosque_id
from database import get_db
from schemas import ActivityCreate, ActivityUpdate
from datetime import datetime

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/")
async def list_activities(upcoming_only: bool = True, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        if upcoming_only:
            rows = await conn.fetch(
                "SELECT * FROM activities WHERE mosque_id = $1 AND date >= $2 ORDER BY date",
                mosque_id,
                datetime.now().date()
            )
        else:
            rows = await conn.fetch("SELECT * FROM activities WHERE mosque_id = $1 ORDER BY date", mosque_id)
        return [dict(row) for row in rows]


@router.get("/{activity_id}")
async def get_activity(activity_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM activities WHERE id = $1 AND mosque_id = $2", activity_id, mosque_id)
        if not row:
            raise HTTPException(404, "Activité introuvable")
        return dict(row)


@router.post("/", status_code=201)
async def create_activity(payload: ActivityCreate, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        data = payload.model_dump()
        row = await conn.fetchrow(
            """INSERT INTO activities (mosque_id, title, description, type, date, time, capacity, speaker, location, livestream_url)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *""",
            mosque_id, data.get('title'), data.get('description'), data.get('type'),
            data.get('date'), data.get('time'), data.get('capacity', 30), data.get('speaker'),
            data.get('location', 'Mosquée'), data.get('livestream_url')
        )
        return dict(row)


@router.patch("/{activity_id}")
async def update_activity(activity_id: int, payload: ActivityUpdate, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not data:
            row = await conn.fetchrow("SELECT * FROM activities WHERE id = $1 AND mosque_id = $2", activity_id, mosque_id)
            if not row:
                raise HTTPException(404, "Activité introuvable")
            return dict(row)

        set_clause = ", ".join([f"{k} = ${i+1}" for i, k in enumerate(data.keys())])
        row = await conn.fetchrow(
            f"UPDATE activities SET {set_clause} WHERE id = ${len(data)+1} AND mosque_id = ${len(data)+2} RETURNING *",
            *data.values(), activity_id, mosque_id
        )
        if not row:
            raise HTTPException(404, "Activité introuvable")
        return dict(row)


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(activity_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM activities WHERE id = $1 AND mosque_id = $2", activity_id, mosque_id)
        if result == "DELETE 0":
            raise HTTPException(404, "Activité introuvable")


@router.get("/{activity_id}/registrations")
async def get_registrations(activity_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        owned = await conn.fetchval("SELECT id FROM activities WHERE id = $1 AND mosque_id = $2", activity_id, mosque_id)
        if not owned:
            raise HTTPException(404, "Activité introuvable")
        rows = await conn.fetch(
            "SELECT r.*, m.first_name, m.username, m.telegram_id FROM registrations r JOIN members m ON r.member_id = m.id WHERE r.activity_id = $1",
            activity_id
        )
        return [dict(row) for row in rows]
