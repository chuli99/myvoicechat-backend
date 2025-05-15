from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.message import ContentType
from app.crud import (
    get_conversation, get_participant_by_user_and_conversation,
    create_message, get_messages_by_conversation_id, 
    get_message, delete_message, mark_messages_as_read
)
from app.schemas import (
    Message, MessageCreate, MessageUpdate, MessageWithSender
)

router = APIRouter()

# Create directory for audio uploads if it doesn't exist
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=Message)
async def create_new_message(
    conversation_id: int,
    content_type: ContentType,
    content: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new message in a conversation"""
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
    
    # Create message data
    message_data = MessageCreate(
        conversation_id=conversation_id,
        content_type=content_type,
    )
    
    # Handle different content types
    if content_type == ContentType.TEXT:
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is required for text messages"
            )
        message_data.content = content
    elif content_type == ContentType.AUDIO:
        if not audio_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file is required for audio messages"
            )
        
        # Save audio file
        file_extension = os.path.splitext(audio_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(await audio_file.read())
        
        # Store the relative path
        media_url = f"uploads/audio/{filename}"
        message_data.media_url = media_url
    
    # Create message
    message = create_message(db, message_data, current_user.id)
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
    
    # Get messages
    messages = get_messages_by_conversation_id(db, conversation_id, skip, limit)
    
    # Mark messages as read
    mark_messages_as_read(db, conversation_id, current_user.id)
    
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message"""
    # Check if message exists
    message = get_message(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if current user is a participant in the conversation
    participant = get_participant_by_user_and_conversation(
        db, current_user.id, message.conversation_id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation"
        )
    
    # Check if current user is the sender
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )
    
    # Delete message
    # If it's an audio message, delete the file as well
    if message.content_type == ContentType.AUDIO and message.media_url:
        file_path = os.path.join(os.getcwd(), message.media_url)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    delete_message(db, message_id)
