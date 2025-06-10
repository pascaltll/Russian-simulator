# models/vocabulary_item.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database.base_class import Base # Asegúrate que la importación de Base es correcta


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id = Column(Integer, primary_key=True, index=True)
    russian_word = Column(String, index=True)
    translation = Column(String)
    example_sentence = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True) # ¡Así debe estar!

    owner = relationship("User", back_populates="vocabulary_items")