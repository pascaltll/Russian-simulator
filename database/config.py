# database/config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

from .base_class import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def init_db():
    import models.user
    import models.audio_submission
    import models.vocabulary_item
    Base.metadata.create_all(bind=get_engine())

def get_db() -> Generator:
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()