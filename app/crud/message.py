from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from app.models.message import Message, ContentType
from app.schemas.message import MessageCreate, MessageUpdate
from app.services.file_storage import FileStorageService


def get_message(db: Session, message_id: int) -> Optional[Message]:
    return db.query(Message).filter(Message.id == message_id).first()


def get_messages(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    return db.query(Message).offset(skip).limit(limit).all()


def create_message(db: Session, message: MessageCreate, sender_id: int) -> Message:
    db_message = Message(
        **message.dict(),
        sender_id=sender_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_message(
    db: Session, message: Message, message_update: MessageUpdate
) -> Message:
    obj_data = jsonable_encoder(message)
    update_data = message_update.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(message, field, update_data[field])
            
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def delete_message(db: Session, message_id: int) -> bool:
    message = get_message(db, message_id)
    if message:
        db.delete(message)
        db.commit()
        return True
    return False


def get_messages_by_conversation_id(
    db: Session, conversation_id: int, skip: int = 0, limit: int = 100
) -> List[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def mark_messages_as_read(db: Session, conversation_id: int, user_id: int) -> int:
    """Mark all messages in a conversation as read for a specific user"""
    result = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
        .update({"is_read": True})
    )
    db.commit()
    return result


def count_unread_messages(db: Session, conversation_id: int, user_id: int) -> int:
    """Count unread messages in a conversation for a specific user"""
    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
        .count()
    )


def create_audio_message(
    db: Session, 
    conversation_id: int, 
    sender_id: int, 
    media_url: str,
    content: Optional[str] = None
) -> Message:
    """Create a new audio message"""
    db_message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content_type=ContentType.AUDIO,
        content=content or "",  # Puede estar vacío para mensajes de solo audio
        media_url=media_url,
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_audio_message(db: Session, message_id: int) -> bool:
    """Delete an audio message and its associated file"""
    message = get_message(db, message_id)
    if message and message.content_type == ContentType.AUDIO and message.media_url:
        # Eliminar el archivo físico
        file_storage = FileStorageService()
        file_path = file_storage.get_full_path_from_url(message.media_url)
        file_storage.delete_audio_file(file_path)
        
        # Eliminar el mensaje de la base de datos
        db.delete(message)
        db.commit()
        return True
    return False


def get_audio_messages_by_conversation(
    db: Session, conversation_id: int, skip: int = 0, limit: int = 100
) -> List[Message]:
    """Get all audio messages from a conversation"""
    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.content_type == ContentType.AUDIO
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
