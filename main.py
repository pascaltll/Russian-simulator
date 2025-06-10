# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging
import os

from database.config import init_db

# Corrected imports for routers: import the 'router' object directly
from routers.auth import router as auth_router
from routers.audio import router as audio_router
from routers.vocabulary import router as vocabulary_router
from routers.grammar import router as grammar_router # ¡AÑADE ESTA LÍNEA!

# from utils.whisper_transcriber import load_whisper_model # REMOVED: No longer needed

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application...")
    init_db()
    # load_whisper_model() # REMOVED: Whisper model is now loaded on module import
    logger.info("Database and Whisper model initialized (or will be on first use).")
    yield
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="Language Simulator MVP",
    description="Backend for audio transcription and vocabulary management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use the correctly imported and renamed router objects
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(audio_router, prefix="/api/audio", tags=["Audio Transcription"])
app.include_router(vocabulary_router, prefix="/api/vocabulary", tags=["Vocabulary Management"])
app.include_router(grammar_router, prefix="/api/grammar", tags=["Grammar Check"]) # ¡AÑADE ESTA LÍNEA!

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse("static/index.html")