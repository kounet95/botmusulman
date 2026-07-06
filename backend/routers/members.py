from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_mosque_id
from database import get_db

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/")
async def list_members(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT m.*, np.* FROM members m LEFT JOIN notification_preferences np ON m.id = np.member_id WHERE m.mosque_id = $1 ORDER BY m.joined_at DESC",
            mosque_id
        )
        return [dict(row) for row in rows]


@router.get("/stats")
async def member_stats(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM members WHERE mosque_id = $1", mosque_id)
        reg_count = await conn.fetchval(
            "SELECT COUNT(*) FROM registrations r JOIN activities a ON r.activity_id = a.id WHERE a.mosque_id = $1",
            mosque_id
        )
        return {
            "total_members": total or 0,
            "total_registrations": reg_count or 0,
        }


@router.delete("/{member_id}", status_code=204)
async def delete_member(member_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM members WHERE id = $1 AND mosque_id = $2", member_id, mosque_id)
        if result == "DELETE 0":
            raise HTTPException(404, "Membre introuvable")
