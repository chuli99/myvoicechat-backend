from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.crud import (
    create_conversation, get_conversation, get_conversations_by_user_id,
    delete_conversation, create_participant, get_participant_by_user_and_conversation
)
from app.schemas import (
    Conversation, ConversationCreate, ConversationDetail,
    ParticipantCreate, User as UserSchema
)

router = APIRouter()


@router.post("/", response_model=Conversation)
def create_new_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation and add the current user as a participant"""
    # Create a new conversation
    conversation = create_conversation(db, ConversationCreate())
    
    # Add the current user as a participant
    participant_data = ParticipantCreate(
        user_id=current_user.id,
        conversation_id=conversation.id
    )
    create_participant(db, participant_data)
    
    return conversation


@router.get("/", response_model=List[Conversation])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    conversations = get_conversations_by_user_id(db, current_user.id)
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with its participants and messages"""
    # Check if conversation exists
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check if current user is a participant
    participant = get_participant_by_user_and_conversation(
        db, current_user.id, conversation_id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation"
        )
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    # Check if conversation exists
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check if current user is a participant
    participant = get_participant_by_user_and_conversation(
        db, current_user.id, conversation_id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation"
        )
    
    # Delete the conversation (this will cascade delete participants and messages)
    delete_conversation(db, conversation_id)
