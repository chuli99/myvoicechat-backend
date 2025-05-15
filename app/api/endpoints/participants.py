from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.crud import (
    get_conversation, get_participant_by_user_and_conversation,
    create_participant, delete_participant, get_participants_by_conversation_id,
    get_user, get_user_by_username, get_participant
)
from app.schemas import (
    ParticipantCreate, ParticipantWithUser,
    User as UserSchema
)

router = APIRouter()


@router.post("/", response_model=ParticipantWithUser)
def add_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a user to a conversation"""
    # Check if conversation exists
    conversation = get_conversation(db, participant_data.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check if current user is a participant
    current_participant = get_participant_by_user_and_conversation(
        db, current_user.id, participant_data.conversation_id
    )
    if not current_participant and current_user.id != participant_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation"
        )
    
    # Check if user exists
    user_to_add = get_user(db, participant_data.user_id)
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {participant_data.user_id} not found"
        )
    
    # Check if user is already a participant
    existing_participant = get_participant_by_user_and_conversation(
        db, participant_data.user_id, participant_data.conversation_id
    )
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant in this conversation"
        )
    
    # Add user to conversation
    new_participant = create_participant(db, participant_data)
    
    # Create response with user data
    participant_with_user = ParticipantWithUser.from_orm(new_participant)
    participant_with_user.user = UserSchema.from_orm(user_to_add)
    
    return participant_with_user


@router.get("/conversation/{conversation_id}", response_model=List[ParticipantWithUser])
def get_participants(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all participants in a conversation"""
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
    
    # Get all participants
    participants = get_participants_by_conversation_id(db, conversation_id)
    
    # Create response with user data
    result = []
    for p in participants:
        user = get_user(db, p.user_id)
        participant_with_user = ParticipantWithUser.from_orm(p)
        participant_with_user.user = UserSchema.from_orm(user)
        result.append(participant_with_user)
    
    return result


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a participant from a conversation"""
    # Get the participant to remove
    participant = get_participant(db, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Check if current user is a participant in the same conversation
    current_participant = get_participant_by_user_and_conversation(
        db, current_user.id, participant.conversation_id
    )
    if not current_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation"
        )
    
    # Only the user themselves or the conversation creator can remove a participant
    if current_user.id != participant.user_id and current_participant.id != min(
        p.id for p in get_participants_by_conversation_id(db, participant.conversation_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove this participant"
        )
    
    # Remove participant
    delete_participant(db, participant_id)
