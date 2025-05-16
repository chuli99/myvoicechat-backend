from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.message import ContentType
from app.schemas import (
    Message, MessageWithSender
)
from app.services.messages_service import MessagesService
from fastapi import Form
router = APIRouter()

# Create directory for audio uploads if it doesn't exist
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=Message)
async def create_new_message(
    conversation_id: int = Form(...),
    content_type: ContentType = Form(...),
    content: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new message in a conversation"""
    message = await MessagesService.create_new_message(db, conversation_id, content_type, content, audio_file, current_user.id)
    return message


@router.get("/conversation/{conversation_id}", response_model=List[MessageWithSender])
def read_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a conversation"""
    messages = MessagesService.read_messages(db, conversation_id, skip, limit, current_user.id)
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message"""
    MessagesService.delete_message(db, message_id, current_user.id)
