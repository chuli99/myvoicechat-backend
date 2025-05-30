from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas import TranslatedMessage
from app.crud.translated_message import translated_message_crud
from app.crud.message import get_message
from app.crud.participant import get_participant_by_user_and_conversation

router = APIRouter()


@router.get("/message/{message_id}", response_model=Optional[TranslatedMessage])
def get_translated_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the translated version of a message"""
    # First, verify the message exists and user has access
    message = get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    # Check if user is participant in the conversation
    participant = get_participant_by_user_and_conversation(db, current_user.id, message.conversation_id)
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
    
    # Get the translated message
    translated_message = translated_message_crud.get_by_original_message_id(db, message_id)
    return translated_message
