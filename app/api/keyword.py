from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.deps import get_keyword_content_generator, get_keyword_service
from app.schemas import KeywordCreate, KeywordRead, KeywordReadDetailed, KeywordUpdate
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

    Also generates 6 pictures, selects the best one, generates voice clips,
    and stores all the information in the database.
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

    # Generate content in the background
    background_tasks.add_task(
        content_generator.generate_content_for_keyword, db_keyword
    )

    return db_keyword


@router.get("/{keyword_id}", response_model=KeywordReadDetailed)
def get_keyword(
    keyword_id: int, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """Get a keyword by ID."""
    db_keyword = keyword_service.get_by_id(keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found",
        )
    return db_keyword


@router.get("/", response_model=List[KeywordRead])
def list_keywords(
    skip: int = 0,
    limit: int = 100,
    keyword_service: KeywordService = Depends(get_keyword_service),
):
    """Get a list of keywords."""
    return keyword_service.list(skip=skip, limit=limit)


@router.patch("/{keyword_id}", response_model=KeywordRead)
def update_keyword(
    keyword_id: int,
    keyword: KeywordUpdate,
    keyword_service: KeywordService = Depends(get_keyword_service),
):
    """Update a keyword."""
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

    return keyword_service.update(keyword_id, keyword)


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: int, keyword_service: KeywordService = Depends(get_keyword_service)
):
    """Delete a keyword."""
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
    """Get a keyword by name."""
    db_keyword = keyword_service.get_by_name(name)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with name '{name}' not found",
        )
    return db_keyword
