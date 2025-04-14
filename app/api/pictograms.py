from fastapi import APIRouter

from app.services import generate_pictogram

router = APIRouter(prefix="/pictograms", tags=["pictograms"])


@router.get("/pictograms")
def get_pictograms():
    return {"message": "Hello, World!"}


@router.post("/pictogram")
def generate_pictogram_endpoint(keyword: str):
    generate_pictogram(keyword)
    return {"message": "Pictogram generated successfully"}
