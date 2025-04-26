from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.models import Voice
from app.services.voice_generator import generate_voice

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/generate", tags=["generation"])
async def generate_voice_endpoint(
    text: str,
    voice: Voice = Query(
        ..., description="Voice type: MAN, WOMAN, MAN_FLEMISH, or WOMAN_FLEMISH"
    ),
):
    """
    Generate voice audio for the provided text using the specified voice type.

    Returns a JSON response with the audio file URL or an error message.

    Available voices:
    - MAN: Adult male voice (English)
    - WOMAN: Adult female voice (English)
    - MAN_FLEMISH: Adult male voice (Flemish)
    - WOMAN_FLEMISH: Adult female voice (Flemish)
    """
    try:
        # Generate voice and get file path
        audio_path = generate_voice(text, voice)

        if not audio_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate voice audio",
            )

        # Return the audio file path
        return JSONResponse(
            content={
                "success": True,
                "audio_path": audio_path,
                "message": f"Voice generated successfully with {voice.name}",
            }
        )

    except Exception as e:
        # Handle any unexpected errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Error generating voice: {str(e)}",
            },
        )
