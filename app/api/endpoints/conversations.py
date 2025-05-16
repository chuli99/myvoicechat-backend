from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.conversations_service import ConversationsService
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
    conversation = ConversationsService.create_new_conversation(db, current_user.id)
    return conversation


@router.get("/", response_model=List[Conversation])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    conversations = ConversationsService.read_conversations(db, current_user.id)
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with its participants and messages"""
    conversation = ConversationsService.read_conversation(db, conversation_id, current_user.id)
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    ConversationsService.delete_conversation(db, conversation_id, current_user.id)
