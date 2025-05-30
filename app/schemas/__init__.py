from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationInDBBase
from app.schemas.participant import Participant, ParticipantCreate
from app.schemas.message import Message, MessageCreate, MessageUpdate
from app.schemas.translated_message import TranslatedMessage, TranslatedMessageCreate, TranslateRequest, TranslateResponse

from pydantic import BaseModel
from typing import List

# Define the complex types with forward references here to avoid circular imports
class ParticipantWithUser(Participant):
    user: User
    
    class Config:
        orm_mode = True


class MessageWithSender(Message):
    sender: User = None
    
    class Config:
        orm_mode = True


class ConversationWithParticipants(Conversation):
    participants: List[Participant] = []
    
    class Config:
        orm_mode = True
    
    
class ConversationWithMessages(Conversation):
    messages: List[Message] = []
    
    class Config:
        orm_mode = True


class ConversationDetail(Conversation):
    participants: List[Participant] = []
    messages: List[Message] = []
    
    class Config:
        orm_mode = True