from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from app.models.participant import Participant
from app.schemas.participant import ParticipantCreate, ParticipantUpdate


def get_participant(db: Session, participant_id: int) -> Optional[Participant]:
    return db.query(Participant).filter(Participant.id == participant_id).first()


def get_participants(db: Session, skip: int = 0, limit: int = 100) -> List[Participant]:
    return db.query(Participant).offset(skip).limit(limit).all()


def create_participant(db: Session, participant: ParticipantCreate) -> Participant:
    db_participant = Participant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


def update_participant(
    db: Session, participant: Participant, participant_update: ParticipantUpdate
) -> Participant:
    obj_data = jsonable_encoder(participant)
    update_data = participant_update.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(participant, field, update_data[field])
            
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def delete_participant(db: Session, participant_id: int) -> bool:
    participant = get_participant(db, participant_id)
    if participant:
        db.delete(participant)
        db.commit()
        return True
    return False


def get_participants_by_conversation_id(db: Session, conversation_id: int) -> List[Participant]:
    return db.query(Participant).filter(Participant.conversation_id == conversation_id).all()


def get_participants_by_user_id(db: Session, user_id: int) -> List[Participant]:
    return db.query(Participant).filter(Participant.user_id == user_id).all()


def get_participant_by_user_and_conversation(
    db: Session, user_id: int, conversation_id: int
) -> Optional[Participant]:
    return (
        db.query(Participant)
        .filter(
            Participant.user_id == user_id,
            Participant.conversation_id == conversation_id
        )
        .first()
    )
