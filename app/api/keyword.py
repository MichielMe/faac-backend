from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.deps import get_keyword_content_generator, get_keyword_service
from app.models import Audio
from app.schemas import (
    KeywordAudioResponse,
    KeywordCreate,
    KeywordRead,
    KeywordReadDetailed,
    KeywordUpdate,
)
from app.services import KeywordContentGenerator, KeywordService

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("/", response_model=KeywordRead, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword: KeywordCreate,
    background_tasks: BackgroundTasks,
    keyword_service: KeywordService = Depends(get_keyword_service),
    content_generator: KeywordContentGenerator = Depends(get_keyword_content_generator),
):
    """
    Create a new keyword.

    Also generates pictograms, selects the best one, generates voice clips,
    and stores all the information in Supabase.
    """
    # Check if keyword with this name already exists
    db_keyword = keyword_service.get_by_name(keyword.name)
    if db_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keyword with name '{keyword.name}' already exists",
        )

    # Create the keyword first
    db_keyword = keyword_service.create(keyword)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create keyword in database",
        )

    # Generate content in the background
    background_tasks.add_task(
        content_generator.generate_content_for_keyword, db_keyword
    )

    return db_keyword


@router.get("/{keyword_id}", response_model=KeywordReadDetailed)
def get_keyword(
    keyword_id: int, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """Get a keyword by ID with detailed information including audio data."""
    db_keyword = keyword_service.get_by_id(keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found",
        )

    # Convert to dictionary to properly handle the audio relationship
    result = _prepare_keyword_response(db_keyword)
    return result


@router.get("/", response_model=List[KeywordRead])
def list_keywords(
    skip: int = 0,
    limit: int = 100,
    keyword_service: KeywordService = Depends(get_keyword_service),
):
    """Get a paginated list of keywords from Supabase."""
    return keyword_service.list(skip=skip, limit=limit)


@router.patch("/{keyword_id}", response_model=KeywordRead)
def update_keyword(
    keyword_id: int,
    keyword: KeywordUpdate,
    keyword_service: KeywordService = Depends(get_keyword_service),
):
    """Update a keyword in Supabase by ID."""
    # Check if keyword exists
    db_keyword = keyword_service.get_by_id(keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found",
        )

    # Check if updating name and new name already exists
    if keyword.name and keyword.name != db_keyword.name:
        existing_keyword = keyword_service.get_by_name(keyword.name)
        if existing_keyword and existing_keyword.id != keyword_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Keyword with name '{keyword.name}' already exists",
            )

    # Update the keyword
    updated_keyword = keyword_service.update(keyword_id, keyword)
    if not updated_keyword:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update keyword with ID {keyword_id}",
        )

    return updated_keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: int, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """Delete a keyword from Supabase by ID."""
    success = keyword_service.delete(keyword_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found",
        )
    return None


@router.get("/name/{name}", response_model=KeywordReadDetailed)
def get_keyword_by_name(
    name: str, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """Get a keyword by name with detailed information including audio data."""
    db_keyword = keyword_service.get_by_name(name)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with name '{name}' not found",
        )

    # Convert to dictionary to properly handle the audio relationship
    result = _prepare_keyword_response(db_keyword)
    return result


@router.get("/audio/{name}", response_model=KeywordAudioResponse)
def get_keyword_with_audio(
    name: str, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """
    Get a keyword by name with simplified format and audio URLs.

    Returns only essential fields: id, name, language, pictogram_url, audio_id,
    and the voice URLs extracted from the audio record.
    """
    result = keyword_service.get_keyword_with_audio_urls(name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with name '{name}' not found",
        )

    return result


def _prepare_keyword_response(keyword) -> Dict:
    """
    Prepare a keyword response with properly formatted audio data.
    This prevents RelationshipInfo validation errors.
    """
    # Convert to dictionary
    data = keyword.model_dump()

    # Handle audio explicitly
    if hasattr(keyword, "audio") and keyword.audio is not None:
        # Check if it's a proper Audio model instance
        if isinstance(keyword.audio, Audio):
            # Convert Audio model to dict
            data["audio"] = {
                "id": keyword.audio.id,
                "keyword_id": keyword.audio.keyword_id,
                "created_at": keyword.audio.created_at,
                "voice_man": keyword.audio.voice_man,
                "voice_woman": keyword.audio.voice_woman,
            }
        elif isinstance(keyword.audio, dict):
            # Use the dictionary directly
            data["audio"] = keyword.audio
        else:
            # Set to None if it's some other unexpected type
            data["audio"] = None
    else:
        data["audio"] = None

    return data
