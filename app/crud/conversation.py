from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
    return db.query(Conversation).offset(skip).limit(limit).all()


def create_conversation(db: Session, conversation: ConversationCreate) -> Conversation:
    db_conversation = Conversation()
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def update_conversation(
    db: Session, conversation: Conversation, conversation_update: ConversationUpdate
) -> Conversation:
    obj_data = jsonable_encoder(conversation)
    update_data = conversation_update.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(conversation, field, update_data[field])
            
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: int) -> bool:
    conversation = get_conversation(db, conversation_id)
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False


def get_conversations_by_user_id(db: Session, user_id: int) -> List[Conversation]:
    return (
        db.query(Conversation)
        .join(Conversation.participants)
        .filter_by(user_id=user_id)
        .all()
    )


def get_all_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """Obtener todas las conversaciones ordenadas por fecha de actualización"""
    return (
        db.query(Conversation)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
