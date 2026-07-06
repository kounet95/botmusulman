import re

from fastapi import APIRouter, Depends, HTTPException

from auth import create_access_token, get_current_admin, hash_password, verify_password
from database import get_db
from schemas import LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "mosquee"


@router.post("/signup", status_code=201)
async def signup(payload: SignupRequest):
    pool = await get_db()
    async with pool.acquire() as conn:
        existing_admin = await conn.fetchval("SELECT id FROM admin_users WHERE email = $1", payload.email)
        if existing_admin:
            raise HTTPException(409, "Un compte existe déjà avec cet email")

        base_slug = _slugify(payload.mosque_name)
        slug = base_slug
        suffix = 2
        while await conn.fetchval("SELECT id FROM mosques WHERE slug = $1", slug):
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        async with conn.transaction():
            mosque = await conn.fetchrow(
                """INSERT INTO mosques (name, city, country, slug, onboarding_completed)
                   VALUES ($1, $2, $3, $4, false)
                   RETURNING id, name, city, country, slug, onboarding_completed""",
                payload.mosque_name, payload.city, payload.country, slug,
            )
            admin = await conn.fetchrow(
                "INSERT INTO admin_users (mosque_id, email, password_hash, full_name) VALUES ($1, $2, $3, $4) RETURNING id",
                mosque["id"], payload.email, hash_password(payload.password), payload.full_name,
            )

        token = create_access_token(admin["id"], mosque["id"], payload.email)
        return {"access_token": token, "token_type": "bearer", "mosque": dict(mosque)}


@router.post("/login")
async def login(payload: LoginRequest):
    pool = await get_db()
    async with pool.acquire() as conn:
        admin = await conn.fetchrow(
            "SELECT a.id, a.password_hash, a.mosque_id, m.name, m.city, m.country, m.slug, m.onboarding_completed "
            "FROM admin_users a JOIN mosques m ON a.mosque_id = m.id WHERE a.email = $1",
            payload.email,
        )
        if not admin or not verify_password(payload.password, admin["password_hash"]):
            raise HTTPException(401, "Email ou mot de passe incorrect")

        token = create_access_token(admin["id"], admin["mosque_id"], payload.email)
        mosque = {
            "id": admin["mosque_id"],
            "name": admin["name"],
            "city": admin["city"],
            "country": admin["country"],
            "slug": admin["slug"],
            "onboarding_completed": admin["onboarding_completed"],
        }
        return {"access_token": token, "token_type": "bearer", "mosque": mosque}


@router.get("/me")
async def me(current_admin: dict = Depends(get_current_admin)):
    pool = await get_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT a.id AS admin_id, a.email, a.full_name, m.id AS mosque_id, m.name, m.city, m.country, m.slug, m.onboarding_completed "
            "FROM admin_users a JOIN mosques m ON a.mosque_id = m.id WHERE a.id = $1",
            current_admin["admin_id"],
        )
        if not row:
            raise HTTPException(404, "Compte introuvable")
        return {
            "admin": {"id": row["admin_id"], "email": row["email"], "full_name": row["full_name"]},
            "mosque": {
                "id": row["mosque_id"],
                "name": row["name"],
                "city": row["city"],
                "country": row["country"],
                "slug": row["slug"],
                "onboarding_completed": row["onboarding_completed"],
            },
        }
