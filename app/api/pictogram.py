
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.pictogram_generator_ideogram import generate_pictogram_ideogram


class PictogramRequest(BaseModel):
    """Request model for pictogram generation."""

    keyword: str


class PictogramResponse(BaseModel):
    """Response model for pictogram generation."""

    success: bool
    message: str
    file_paths: list[str] = []


router = APIRouter(prefix="/pictogram", tags=["pictogram"])


@router.post(
    "/generate/ideogram", response_model=PictogramResponse, tags=["generation"]
)
async def generate_ideogram_pictogram(request: PictogramRequest):
    """
    Generate pictograms using Ideogram AI.

    This endpoint generates four pictograms for the provided keyword using Ideogram AI.
    The images are stored in the assets directory and the paths are returned.
    """
    try:
        if not request.keyword or len(request.keyword.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keyword cannot be empty",
            )

        result = generate_pictogram_ideogram(keyword=request.keyword)

        return PictogramResponse(
            success=True,
            message=f"Successfully generated pictograms for '{request.keyword}'",
            file_paths=result.get("file_paths", []) if isinstance(result, dict) else [],
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=PictogramResponse(
                success=False,
                message=f"Error generating pictograms: {str(e)}",
                file_paths=[],
            ).model_dump(),
        )


@router.post("/generate/four", response_model=PictogramResponse, tags=["generation"])
async def generate_four_pictograms(request: PictogramRequest):
    """
    Generate four pictograms for a keyword.

    This endpoint generates four pictograms using Ideogram AI and returns their file paths.
    In the future, this endpoint could be extended to use multiple sources.
    """
    try:
        if not request.keyword or len(request.keyword.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keyword cannot be empty",
            )

        result = generate_pictogram_ideogram(keyword=request.keyword)

        return PictogramResponse(
            success=True,
            message=f"Successfully generated four pictograms for '{request.keyword}'",
            file_paths=result.get("file_paths", []) if isinstance(result, dict) else [],
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=PictogramResponse(
                success=False,
                message=f"Error generating pictograms: {str(e)}",
                file_paths=[],
            ).model_dump(),
        )
