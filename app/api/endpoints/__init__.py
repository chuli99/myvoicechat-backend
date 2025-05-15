from fastapi import APIRouter
from app.api.endpoints import users, conversations, participants, messages

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(participants.router, prefix="/participants", tags=["participants"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])