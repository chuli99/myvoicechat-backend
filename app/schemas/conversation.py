from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ConversationBase(BaseModel):
    pass


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    pass


class ConversationInDBBase(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Conversation(ConversationInDBBase):
    pass
