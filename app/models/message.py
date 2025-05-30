from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class ContentType(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    content = Column(String)
    media_url = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    is_read = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    translated_message = relationship("TranslatedMessage", back_populates="original_message", uselist=False)
