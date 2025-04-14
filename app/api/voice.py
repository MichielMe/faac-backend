from fastapi import APIRouter

from app.services import generate_voice

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/generate-voice")
async def generate_voice_endpoint(text: str):
    return generate_voice(text)
