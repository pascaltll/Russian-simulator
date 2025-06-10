from sqlalchemy.orm import Session
from models.user import User
from models.audio_submission import AudioSubmission # Asegúrate de que AudioSubmission ya tenga la columna 'language'
from models.vocabulary_item import VocabularyItem
from schemas.user import UserCreate, UserCreateTelegram
from schemas.audio_submission import AudioSubmissionCreate # Asegúrate de que AudioSubmissionCreate ya tenga el campo 'language'
from schemas.vocabulary_item import VocabularyItemCreate
from typing import List, Optional

# --- User CRUD Operations ---
def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_telegram_user(db: Session, user_data: UserCreateTelegram) -> User:
    db_user = User(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        email=user_data.email, # Asegúrate de que el modelo User soporte email nullable si es el caso
        hashed_password=user_data.hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Audio Submission CRUD Operations ---
def create_audio_submission(db: Session, submission: AudioSubmissionCreate, user_id: int) -> AudioSubmission:
    # submission.dict() ahora incluirá 'language' si lo añadiste a AudioSubmissionCreate
    db_submission = AudioSubmission(**submission.model_dump(), user_id=user_id) # Usar model_dump() para Pydantic v2+
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# MODIFICACIÓN CLAVE AQUÍ: limit ahora puede ser None
def get_audio_submissions_by_user(db: Session, user_id: int, offset: int = 0, limit: Optional[int] = 5) -> List[AudioSubmission]:
    query = db.query(AudioSubmission).filter(AudioSubmission.user_id == user_id).order_by(AudioSubmission.created_at.desc()).offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()

def delete_audio_submission(db: Session, audio_id: int, user_id: int) -> bool:
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
def create_vocabulary_item(db: Session, item: VocabularyItemCreate, user_id: Optional[int] = None) -> VocabularyItem:
    db_item_data = item.model_dump() # Usar model_dump() para Pydantic v2+
    if user_id:
        db_item_data["user_id"] = user_id
    db_item = VocabularyItem(**db_item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_all_vocabulary_items(db: Session) -> List[VocabularyItem]:
    return db.query(VocabularyItem).all()

def get_vocabulary_items_by_user(db: Session, user_id: int) -> List[VocabularyItem]:
    return db.query(VocabularyItem).filter(VocabularyItem.user_id == user_id).order_by(VocabularyItem.created_at.desc()).all()

def delete_vocabulary_item(db: Session, item_id: int, user_id: int) -> bool:
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id, VocabularyItem.user_id == user_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False