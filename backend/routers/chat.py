from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.quran_chat import format_answer, rechercher_versets

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/quran")
def ask_quran(payload: ChatRequest):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Pose une question valide.")

    results = rechercher_versets(question, n=3)
    if not results:
        return {
            "answer": "❌ Je n’ai pas trouvé de verset correspondant. Essaie avec un nom de sourate, un numéro comme 2:255, ou un mot-clé en poular ou en français.",
            "results": [],
        }

    best = results[0]
    return {
        "answer": format_answer(question, best),
        "results": [
            {
                "sourate": item.get("sourate"),
                "verset": item.get("verset"),
                "sourate_nom": item.get("sourate_nom"),
                "arabe": item.get("arabe"),
                "traduction": item.get("traduction"),
            }
            for item in results
        ],
    }
