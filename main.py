"""
Main application entry point for the Language Simulator MVP backend.

This module configures the FastAPI app, loads routers for authentication,
audio transcription, vocabulary management, and grammar checking,
and sets up middleware and static file serving.
"""

from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database.config import init_db
from routers.auth import router as auth_router
from routers.audio import router as audio_router
from routers.vocabulary import router as vocabulary_router
from routers.grammar import router as grammar_router

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    """
    Asynchronous context manager for managing the FastAPI application's lifespan.
    Initializes the database at startup and logs shutdown messages.

    Args:
        _fastapi_app (FastAPI): The FastAPI application instance (unused).
    """
    logger.info("Starting FastAPI application...")
    init_db()  # Initialize the database tables if they don't exist
    logger.info(
        "Database initialized. "
        "Whisper model will be loaded on first use (if not already)."
    )
    yield  # Application remains running during this yield
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="Language Simulator MVP",
    description=(
        "Backend for audio transcription, vocabulary management, "
        "and grammar check"
    ),
    version="1.0.0",
    lifespan=lifespan  # Assign the lifespan context manager
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(audio_router, prefix="/api/audio", tags=["Audio Transcription"])
app.include_router(
    vocabulary_router,
    prefix="/api/vocabulary",
    tags=["Vocabulary Management"]
)
app.include_router(grammar_router, prefix="/api/grammar", tags=["Grammar Check"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serves the main HTML file for the application.

    Returns:
        FileResponse: The index.html file from the static directory.
    """
    return FileResponse("static/index.html")
