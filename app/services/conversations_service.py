from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.crud import (
    create_conversation, get_conversation, get_conversations_by_user_id,
    delete_conversation, create_participant, get_participant_by_user_and_conversation,
    get_participants_by_conversation_id
)
from app.schemas import ConversationCreate, ParticipantCreate

class ConversationsService:
    @staticmethod
    def create_new_conversation(db: Session, current_user_id: int):
        conversation = create_conversation(db, ConversationCreate())
        participant_data = ParticipantCreate(user_id=current_user_id, conversation_id=conversation.id)
        create_participant(db, participant_data)
        return conversation

    @staticmethod
    def read_conversations(db: Session, current_user_id: int):
        conversations = get_conversations_by_user_id(db, current_user_id)
        return conversations

    @staticmethod
    def read_conversation(db: Session, conversation_id: int, current_user_id: int):
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        return conversation

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, current_user_id: int):
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        delete_conversation(db, conversation_id)
