import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import keyword_router, pictogram_router, voice_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup events
    yield
    # Run shutdown events


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Set up CORS
    # Support BACKEND_CORS_ORIGINS as list or JSON/comma-separated string
    cors_origins = settings.BACKEND_CORS_ORIGINS
    if isinstance(cors_origins, str):
        try:
            cors_origins = json.loads(cors_origins)
        except ValueError:
            cors_origins = [
                o.strip() for o in cors_origins.strip("[]").split(",") if o.strip()
            ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = create_application()

# Include routers
app.include_router(keyword_router, prefix=settings.API_V1_STR)
app.include_router(pictogram_router)
app.include_router(voice_router)
# app.include_router(image_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to FAAC Backend API. See /docs for API documentation."}
