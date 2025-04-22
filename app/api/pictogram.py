import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services import generate_pictogram_ideogram

router = APIRouter(prefix="/pictogram", tags=["pictogram"])


@router.post("/generate/ideogram", tags=["generation"])
def generate_ideogram_pictogram(keyword: str):
    """Generate two pictograms using Ideogram"""
    return generate_pictogram_ideogram(keyword)


@router.post("/generate/four", tags=["generation"])
async def generate_four_pictograms(keyword: str):
    """Generate four pictograms for a keyword

    We generate four from Ideogram.

    """
    result = generate_pictogram_ideogram(keyword)
    return JSONResponse(content=result)
