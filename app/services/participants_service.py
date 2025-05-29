from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.crud import (
    get_conversation, get_participant_by_user_and_conversation,
    create_participant, delete_participant, get_participants_by_conversation_id,
    get_user, get_participant
)
from app.schemas import ParticipantCreate

class ParticipantsService:
    @staticmethod
    def add_participant(db: Session, participant_data: ParticipantCreate, current_user_id: int):
        conversation = get_conversation(db, participant_data.conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        current_participant = get_participant_by_user_and_conversation(db, current_user_id, participant_data.conversation_id)
        if not current_participant and current_user_id != participant_data.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        user_to_add = get_user(db, participant_data.user_id)
        if not user_to_add:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {participant_data.user_id} not found")
        existing_participant = get_participant_by_user_and_conversation(db, participant_data.user_id, participant_data.conversation_id)
        if existing_participant:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a participant in this conversation")
        new_participant = create_participant(db, participant_data)
        return new_participant, user_to_add

    @staticmethod
    def get_participants(db: Session, conversation_id: int, current_user_id: int):
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        participants = get_participants_by_conversation_id(db, conversation_id)
        return participants

    @staticmethod
    def remove_participant(db: Session, participant_id: int, current_user_id: int):
        participant = get_participant(db, participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        current_participant = get_participant_by_user_and_conversation(db, current_user_id, participant.conversation_id)
        if not current_participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        # Only the user themselves or the conversation creator can remove a participant
        all_participants = get_participants_by_conversation_id(db, participant.conversation_id)
        if current_user_id != participant.user_id and current_participant.id != min(p.id for p in all_participants):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to remove this participant")
        delete_participant(db, participant_id)

    @staticmethod
    def user_has_access_to_conversation(db: Session, user_id: int, conversation_id: int) -> bool:
        """Check if user has access to a conversation"""
        try:
            participant = get_participant_by_user_and_conversation(db, user_id, conversation_id)
            return participant is not None
        except Exception:
            return False
