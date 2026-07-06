from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_mosque_id
from database import get_db
from schemas import ContentCreate

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/")
async def list_content(content_type: str | None = None, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        if content_type:
            rows = await conn.fetch(
                "SELECT * FROM content_schedule WHERE mosque_id = $1 AND type = $2 ORDER BY scheduled_date DESC",
                mosque_id, content_type
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM content_schedule WHERE mosque_id = $1 ORDER BY scheduled_date DESC",
                mosque_id
            )
        return [dict(row) for row in rows]


@router.post("/", status_code=201)
async def create_content(payload: ContentCreate, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        data = payload.model_dump()
        row = await conn.fetchrow(
            """INSERT INTO content_schedule (mosque_id, type, content_ar, content_fr, source, scheduled_date)
               VALUES ($1, $2, $3, $4, $5, $6) RETURNING *""",
            mosque_id, data.get('type'), data.get('content_ar'), data.get('content_fr'),
            data.get('source'), data.get('scheduled_date')
        )
        return dict(row)


@router.delete("/{content_id}", status_code=204)
async def delete_content(content_id: int, mosque_id: int = Depends(get_current_mosque_id)):
    pool = await get_db()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM content_schedule WHERE id = $1 AND mosque_id = $2", content_id, mosque_id)
        if result == "DELETE 0":
            raise HTTPException(404, "Contenu introuvable")


CONTENT_TEMPLATES = {
    "hadiths": [
        {"content_fr": "Le Prophète ﷺ a dit : « Celui qui croit en Allah et au Jour dernier doit honorer son voisin. »", "source": "Bukhari & Muslim"},
        {"content_fr": "Le Prophète ﷺ a dit : « Les actions ne valent que par leurs intentions. »", "source": "Bukhari"},
        {"content_fr": "Le Prophète ﷺ a dit : « Le sourire à ton frère est une sadaqa. »", "source": "Tirmidhi"},
        {"content_fr": "Le Prophète ﷺ a dit : « Aucun de vous n'est vraiment croyant tant qu'il n'aime pas pour son frère ce qu'il aime pour lui-même. »", "source": "Bukhari & Muslim"},
        {"content_fr": "Le Prophète ﷺ a dit : « La meilleure des aumônes est celle que donne celui qui a peu. »", "source": "Abu Dawud"},
    ],
    "versets": [
        {"content_ar": "إِنَّ مَعَ الْعُسْرِ يُسْرًا", "content_fr": "Certes, avec la difficulté vient la facilité.", "source": "Sourate Al-Inshirah (94:6)"},
        {"content_ar": "وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ", "content_fr": "Quiconque place sa confiance en Allah, Il lui suffit.", "source": "Sourate At-Talaq (65:3)"},
    ],
}


@router.get("/templates")
def get_templates():
    return CONTENT_TEMPLATES
