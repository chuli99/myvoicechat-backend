from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.message import ContentType


class MessageBase(BaseModel):
    conversation_id: int
    sender_id: int
    content_type: ContentType
    content: Optional[str] = None
    media_url: Optional[str] = None
    is_read: bool = False


class MessageCreate(BaseModel):
    conversation_id: int
    content_type: ContentType
    content: Optional[str] = None
    media_url: Optional[str] = None


class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None


class MessageInDBBase(MessageBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Message(MessageInDBBase):
    pass
