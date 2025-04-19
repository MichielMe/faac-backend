from fastapi import APIRouter, Query

from app.models import Voice
from app.services import generate_voice, generate_voice_flemish

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/generate", tags=["generation"])
async def generate_voice_endpoint(
    text: str,
    voice: Voice = Query(
        ..., description="Voice type: man, woman, child, man_vl, or vrouw_vl"
    ),
):
    """
    Generate voice audio for the provided text using the specified voice type.

    Available voices:
    - man: Adult male voice
    - woman: Adult female voice
    - child: Child voice
    - man_vl: Flemish male voice
    - vrouw_vl: Flemish female voice
    """
    if voice == Voice.MAN_FLEMISH or voice == Voice.WOMAN_FLEMISH:
        return generate_voice_flemish(text, voice)
    else:
        return generate_voice(text, voice)
