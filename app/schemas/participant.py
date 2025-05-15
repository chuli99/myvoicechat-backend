from pydantic import BaseModel
from datetime import datetime


class ParticipantBase(BaseModel):
    user_id: int
    conversation_id: int


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(BaseModel):
    pass


class ParticipantInDBBase(ParticipantBase):
    id: int
    joined_at: datetime

    class Config:
        orm_mode = True


class Participant(ParticipantInDBBase):
    pass
