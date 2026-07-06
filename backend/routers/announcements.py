from fastapi import APIRouter, BackgroundTasks, Depends
from auth import get_current_mosque_id
from database import get_db
from schemas import AnnouncementCreate
import httpx
import os

router = APIRouter(prefix="/announcements", tags=["announcements"])

BOT_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN', '')}"


async def _broadcast_telegram(mosque_id: int, text: str):
    pool = await get_db()
    async with pool.acquire() as conn:
        members = await conn.fetch("SELECT telegram_id FROM members WHERE mosque_id = $1", mosque_id)
    async with httpx.AsyncClient() as client:
        for m in members:
            try:
                await client.post(f"{BOT_API_URL}/sendMessage", json={
                    "chat_id": m["telegram_id"],
                    "text": text,
                    "parse_mode": "Markdown",
                })
            except Exception:
                pass


@router.get("/")
async def list_announcements(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM announcements WHERE mosque_id = $1 ORDER BY created_at DESC", mosque_id)
        return [dict(row) for row in rows]


@router.post("/", status_code=201)
async def create_announcement(payload: AnnouncementCreate, background_tasks: BackgroundTasks, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO announcements (title, body, mosque_id) VALUES ($1, $2, $3) RETURNING *",
            payload.title, payload.body, mosque_id
        )
    if payload.send_now:
        text = f"📢 *{payload.title}*\n\n{payload.body}"
        background_tasks.add_task(_broadcast_telegram, mosque_id, text)
    return dict(row)
