"""
Module for CRUD (Create, Read, Update, Delete) operations
on database models such as users, audio submissions,
and vocabulary items.
"""
# Group 1: Standard libraries
from typing import List, Optional

# Group 2: Third-party libraries
from sqlalchemy.orm import Session # Corrected import order (C0411)

# Group 3: First-party modules
from models.user import User
from models.audio_submission import AudioSubmission
from models.vocabulary_item import VocabularyItem
from schemas.user import UserCreate, UserCreateTelegram
from schemas.audio_submission import AudioSubmissionCreate
from schemas.vocabulary_item import VocabularyItemCreate


# --- User CRUD Operations ---
def get_by_username(db: Session, username: str) -> Optional[User]:
    """
    Retrieves a user by their username.

    Args:
        db (Session): The database session.
        username (str): The username to search for.

    Returns:
        Optional[User]: The User object if found, otherwise None.
    """
    # C0301: Line too long - Not applicable to this line.
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    """
    Creates a new user in the database.

    Args:
        db (Session): The database session.
        user (UserCreate): User data from the creation schema.
        hashed_password (str): The already hashed user password.

    Returns:
        User: The newly created and persisted User object in the database.
    """
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """
    Retrieves a user by their Telegram ID.

    Args:
        db (Session): The database session.
        telegram_id (int): The Telegram ID to search for.

    Returns:
        Optional[User]: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_telegram_user(db: Session, user_data: UserCreateTelegram) -> User:
    """
    Creates a new Telegram user in the database.

    Args:
        db (Session): The database session.
        user_data (UserCreateTelegram): Telegram user data from the schema.

    Returns:
        User: The newly created and persisted User object in the database.
    """
    # C0301: Line too long - Corrected by splitting the line
    db_user = User(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Audio Submission CRUD Operations ---
def create_audio_submission(
    db: Session, submission: AudioSubmissionCreate, user_id: int
) -> AudioSubmission:
    """
    Creates a new audio submission in the database associated with a user.

    Args:
        db (Session): The database session.
        submission (AudioSubmissionCreate): Audio submission data from the schema.
        user_id (int): The ID of the user to whom the audio submission belongs.

    Returns:
        AudioSubmission: The newly created and persisted AudioSubmission object.
    """
    # C0301: Line too long - Corrected by splitting the line
    db_submission = AudioSubmission(**submission.model_dump(), user_id=user_id)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def get_audio_submissions_by_user(
    db: Session, user_id: int, offset: int = 0, limit: Optional[int] = 5
) -> List[AudioSubmission]:
    """
    Retrieves audio submissions for a specific user, with pagination.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        offset (int): The number of records to skip from the start.
        limit (Optional[int]): The maximum number of records to return.
                                If None, returns all records.

    Returns:
        List[AudioSubmission]: A list of AudioSubmission objects.
    """
    # C0301: Line too long - Corrected by splitting the line
    query = db.query(AudioSubmission).filter(
        AudioSubmission.user_id == user_id
    ).order_by(AudioSubmission.created_at.desc()).offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def delete_audio_submission(db: Session, audio_id: int, user_id: int) -> bool:
    """
    Deletes a specific audio submission for a user.

    Args:
        db (Session): The database session.
        audio_id (int): The ID of the audio submission to delete.
        user_id (int): The ID of the user to whom the audio submission belongs.

    Returns:
        bool: True if the audio submission was deleted, False otherwise.
    """
    # C0301: Line too long - Corrected by splitting the line
    submission = db.query(AudioSubmission).filter(
        AudioSubmission.id == audio_id,
        AudioSubmission.user_id == user_id
    ).first()
    if submission:
        db.delete(submission)
        db.commit()
        return True
    return False


# --- Vocabulary Item CRUD Operations ---
def create_vocabulary_item(
    db: Session, item: VocabularyItemCreate, user_id: Optional[int] = None
) -> VocabularyItem:
    """
    Creates a new vocabulary item in the database,
    optionally associated with a user.

    Args:
        db (Session): The database session.
        item (VocabularyItemCreate): Vocabulary item data from the schema.
        user_id (Optional[int]): The ID of the user to whom the item belongs.
                                   Can be None if not associated with a specific user.

    Returns:
        VocabularyItem: The newly created and persisted VocabularyItem object.
    """
    db_item_data = item.model_dump()
    if user_id:
        db_item_data["user_id"] = user_id
    db_item = VocabularyItem(**db_item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_all_vocabulary_items(db: Session) -> List[VocabularyItem]:
    """
    Retrieves all vocabulary items from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[VocabularyItem]: A list of all VocabularyItem objects.
    """
    return db.query(VocabularyItem).all()


def get_vocabulary_items_by_user(db: Session, user_id: int) -> List[VocabularyItem]:
    """
    Retrieves all vocabulary items for a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[VocabularyItem]: A list of VocabularyItem objects for the user.
    """
    # C0301: Line too long - Corrected by splitting the line
    return db.query(VocabularyItem).filter(
        VocabularyItem.user_id == user_id
    ).order_by(VocabularyItem.created_at.desc()).all()


def delete_vocabulary_item(db: Session, item_id: int, user_id: int) -> bool:
    """
    Deletes a specific vocabulary item for a user.

    Args:
        db (Session): The database session.
        item_id (int): The ID of the vocabulary item to delete.
        user_id (int): The ID of the user to whom the item belongs.

    Returns:
        bool: True if the item was deleted, False otherwise.
    """
    # C0301: Line too long - Corrected by splitting the line
    item = db.query(VocabularyItem).filter(
        VocabularyItem.id == item_id,
        VocabularyItem.user_id == user_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
