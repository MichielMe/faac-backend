from fastapi import FastAPI

from app.api import pictograms_router, voice_generator_router

app = FastAPI()

app.include_router(pictograms_router)
app.include_router(voice_generator_router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
