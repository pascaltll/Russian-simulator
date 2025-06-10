"""
Database configuration for the FastAPI application.
Defines the database URL, engine, and session factory.
Also includes the function to initialize the database and obtain sessions.
"""
# Group 1: Standard libraries
import os
from typing import Generator

# Group 2: Third-party libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Group 3: First-party modules
from .base_class import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db"
)

ENGINE = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SESSION_LOCAL_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def init_db():
    """
    Initializes the database, creating all tables defined in the models.
    This is useful for initial setup in development.
    """
    # C0415, W0611: These imports are intentionally inside init_db
    # because they are only needed when Base.metadata.create_all is called,
    # which typically happens once on application startup.
    # Disabling specific Pylint warnings for these lines.
    import models.user # pylint: disable=C0415, W0611
    import models.audio_submission # pylint: disable=C0415, W0611
    import models.vocabulary_item # pylint: disable=C0415, W0611
    Base.metadata.create_all(bind=ENGINE)


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for FastAPI dependencies.
    Ensures that the session is closed after use.

    Yields:
        sqlalchemy.orm.Session: An active database session.
    """
    db = SESSION_LOCAL_FACTORY()
    try:
        yield db
    finally:
        db.close()
