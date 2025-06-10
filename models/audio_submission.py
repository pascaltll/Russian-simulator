# models/audio_submission.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base_class import Base

class AudioSubmission(Base):
    __tablename__ = "audio_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio_path = Column(String)
    original_transcript = Column(String)
    language = Column(String, nullable=True) # 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="audio_submissions")