from sqlalchemy.orm import Session
from app.models.translated_message import TranslatedMessage
from app.schemas.translated_message import TranslatedMessageCreate
from typing import Optional


class TranslatedMessageCRUD:
    @staticmethod
    def create(db: Session, translated_message: TranslatedMessageCreate) -> TranslatedMessage:
        """Create a new translated message"""
        db_translated_message = TranslatedMessage(**translated_message.dict())
        db.add(db_translated_message)
        db.commit()
        db.refresh(db_translated_message)
        return db_translated_message
    
    @staticmethod
    def get_by_original_message_id(db: Session, original_message_id: int) -> Optional[TranslatedMessage]:
        """Get translated message by original message ID"""
        return db.query(TranslatedMessage).filter(
            TranslatedMessage.original_message_id == original_message_id
        ).first()
    
    @staticmethod
    def get_by_id(db: Session, translated_message_id: int) -> Optional[TranslatedMessage]:
        """Get translated message by ID"""
        return db.query(TranslatedMessage).filter(
            TranslatedMessage.id == translated_message_id
        ).first()
    
    @staticmethod
    def delete(db: Session, translated_message_id: int) -> bool:
        """Delete a translated message"""
        translated_message = db.query(TranslatedMessage).filter(
            TranslatedMessage.id == translated_message_id
        ).first()
        if translated_message:
            db.delete(translated_message)
            db.commit()
            return True
        return False


# Create instance
translated_message_crud = TranslatedMessageCRUD()
