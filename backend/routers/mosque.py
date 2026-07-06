import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from auth import get_current_mosque_id
from database import get_db
from schemas import MosqueProfileUpdate

router = APIRouter(prefix="/mosque", tags=["mosque"])

UPLOAD_DIR = "uploads/mosques"
PHOTO_KINDS = {
    "exterior": "exterior_photo_url",
    "interior": "interior_photo_url",
    "logo": "logo_url",
}
REQUIRED_FIELDS = ["installation_type", "name", "address", "city", "postal_code", "country"]


async def _maybe_complete_onboarding(conn, mosque_id: int):
    row = await conn.fetchrow("SELECT * FROM mosques WHERE id = $1", mosque_id)
    data = dict(row)
    has_required = all(data.get(f) for f in REQUIRED_FIELDS)
    has_photos = bool(data.get("exterior_photo_url")) and bool(data.get("interior_photo_url"))
    if has_required and has_photos and not data["onboarding_completed"]:
        await conn.execute("UPDATE mosques SET onboarding_completed = true WHERE id = $1", mosque_id)


@router.get("/profile")
async def get_profile(mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM mosques WHERE id = $1", mosque_id)
        if not row:
            raise HTTPException(404, "Mosquée introuvable")
        return dict(row)


@router.patch("/profile")
async def update_profile(payload: MosqueProfileUpdate, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if data:
            set_clause = ", ".join([f"{k} = ${i + 1}" for i, k in enumerate(data.keys())])
            await conn.execute(
                f"UPDATE mosques SET {set_clause} WHERE id = ${len(data) + 1}",
                *data.values(), mosque_id,
            )
        await _maybe_complete_onboarding(conn, mosque_id)
        row = await conn.fetchrow("SELECT * FROM mosques WHERE id = $1", mosque_id)
        return dict(row)


@router.post("/photo")
async def upload_photo(
    kind: str = Query(..., pattern="^(exterior|interior|logo)$"),
    file: UploadFile = File(...),
    mosque_id: int = Depends(get_current_mosque_id),
):
    column = PHOTO_KINDS[kind]
    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(400, "Format d'image non supporté")

    mosque_dir = os.path.join(UPLOAD_DIR, str(mosque_id))
    os.makedirs(mosque_dir, exist_ok=True)
    filename = f"{kind}-{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(mosque_dir, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    url = f"/uploads/mosques/{mosque_id}/{filename}"

    pool = await get_db()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE mosques SET {column} = $1 WHERE id = $2", url, mosque_id)
        await _maybe_complete_onboarding(conn, mosque_id)

    return {"url": url}
