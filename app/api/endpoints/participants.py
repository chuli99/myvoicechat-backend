from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.participants_service import ParticipantsService
from app.schemas import (
    ParticipantCreate, ParticipantWithUser,
    User as UserSchema
)
from app.crud import get_user

router = APIRouter()


@router.post("/", response_model=ParticipantWithUser)
def add_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a user to a conversation"""
    new_participant, user_to_add = ParticipantsService.add_participant(db, participant_data, current_user.id)
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
    participants = ParticipantsService.get_participants(db, conversation_id, current_user.id)
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
    ParticipantsService.remove_participant(db, participant_id, current_user.id)
