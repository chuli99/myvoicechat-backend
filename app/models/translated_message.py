from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class TranslatedMessage(Base):
    __tablename__ = "translated_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    original_message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True)
    target_language = Column(String, nullable=False)
    translated_content = Column(Text, nullable=True)  # Nullable for audio messages
    media_url = Column(String, nullable=True)  # For TTS audio
    content_type = Column(String, nullable=False, default="TEXT")  # "TEXT" or "AUDIO"
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    original_message = relationship("Message", back_populates="translated_message")
