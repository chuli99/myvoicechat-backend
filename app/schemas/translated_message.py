from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TranslatedMessageBase(BaseModel):
    target_language: str
    translated_content: Optional[str] = None  # Nullable for audio messages
    media_url: Optional[str] = None
    content_type: str = "TEXT"  # "TEXT" or "AUDIO"


class TranslatedMessageCreate(TranslatedMessageBase):
    original_message_id: int


class TranslatedMessage(TranslatedMessageBase):
    id: int
    original_message_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
