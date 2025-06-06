from fastapi import APIRouter
from app.api.endpoints import users, conversations, participants, messages, translations, audio
from app.websockets import endpoints as websocket_endpoints

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(participants.router, prefix="/participants", tags=["participants"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(translations.router, prefix="/translations", tags=["translations"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(websocket_endpoints.router, tags=["websockets"])