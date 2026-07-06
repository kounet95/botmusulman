from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_mosque_id
from database import get_db
from schemas import DonationCampaignCreate

router = APIRouter(prefix="/donations", tags=["donations"])


@router.get("/campaigns")
async def list_campaigns(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM donation_campaigns WHERE mosque_id = $1 ORDER BY created_at DESC", mosque_id)
        return [dict(row) for row in rows]


@router.post("/campaigns", status_code=201)
async def create_campaign(payload: DonationCampaignCreate, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        data = payload.model_dump()
        row = await conn.fetchrow(
            """INSERT INTO donation_campaigns
               (mosque_id, title, description, type, goal_amount, payment_url, orange_money_number, mtn_momo_number)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *""",
            mosque_id, data.get('title'), data.get('description'), data.get('type', 'general'),
            data.get('goal_amount'), data.get('payment_url'),
            data.get('orange_money_number'), data.get('mtn_momo_number')
        )
        return dict(row)


@router.patch("/campaigns/{campaign_id}/toggle")
async def toggle_campaign(campaign_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        camp = await conn.fetchrow("SELECT is_active FROM donation_campaigns WHERE id = $1 AND mosque_id = $2", campaign_id, mosque_id)
        if not camp:
            raise HTTPException(404, "Collecte introuvable")
        new_val = not camp['is_active']
        await conn.execute("UPDATE donation_campaigns SET is_active = $1 WHERE id = $2 AND mosque_id = $3", new_val, campaign_id, mosque_id)
        return {"is_active": new_val}


@router.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM donation_campaigns WHERE id = $1 AND mosque_id = $2", campaign_id, mosque_id)
        if result == "DELETE 0":
            raise HTTPException(404, "Collecte introuvable")
