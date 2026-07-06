from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

from routers import activities, members, content, donations, dashboard, announcements, auth, mosque

os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="MosquéeBot API",
    description="API d'administration pour la plateforme de gestion communautaire islamique",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(activities.router)
app.include_router(members.router)
app.include_router(content.router)
app.include_router(donations.router)
app.include_router(dashboard.router)
app.include_router(announcements.router)
app.include_router(mosque.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "MosquéeBot API"}
