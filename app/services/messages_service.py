import os
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional
from app.crud import (
    get_conversation, get_participant_by_user_and_conversation,
    create_message, get_messages_by_conversation_id, 
    get_message, delete_message, mark_messages_as_read
)
from app.models.message import ContentType
from app.schemas import MessageCreate
from app.services.translation_service import TranslationService
from app.services.file_storage import FileStorageService
import logging

logger = logging.getLogger(__name__)

class MessagesService:
    @staticmethod
    async def create_new_message(db: Session, conversation_id: int, content_type: ContentType, content: Optional[str], audio_file: Optional[UploadFile], current_user_id: int):
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        message_data = MessageCreate(conversation_id=conversation_id, content_type=content_type)
        if content_type == ContentType.TEXT:
            if not content:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content is required for text messages")
            message_data.content = content
        elif content_type == ContentType.AUDIO:
            if not audio_file:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file is required for audio messages")
            
            # Usar FileStorageService para guardar el archivo de audio
            file_service = FileStorageService()
            file_path = await file_service.save_message_audio_file(audio_file, current_user_id, conversation_id)
            
            # Generar URL para el archivo
            media_url = file_service.get_message_file_url(file_path)
            print(f"Audio file saved to {file_path} with URL {media_url}")
            message_data.media_url = media_url
        message = create_message(db, message_data, current_user_id)
        
        # Create translated message automatically for both text and audio messages
        if content_type == ContentType.TEXT and content:
            try:
                translated_message_id = await TranslationService.create_translated_message(db, message)
                if translated_message_id:
                    logger.info(f"Successfully created translated message {translated_message_id} for message {message.id}")
            except Exception as e:
                logger.error(f"Failed to create translated message for message {message.id}: {e}")
                # Don't fail the original message creation if translation fails
        elif content_type == ContentType.AUDIO:
            try:
                translated_message_id = await TranslationService.create_translated_message(db, message)
                if translated_message_id:
                    logger.info(f"Successfully created translated audio message {translated_message_id} for message {message.id}")
            except Exception as e:
                logger.error(f"Failed to create translated audio message for message {message.id}: {e}")
                # Don't fail the original message creation if translation fails
        
        return message

    @staticmethod
    def read_messages(db: Session, conversation_id: int, skip: int, limit: int, current_user_id: int):
        conversation = get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        messages = get_messages_by_conversation_id(db, conversation_id, skip, limit)
        mark_messages_as_read(db, conversation_id, current_user_id)
        return messages

    @staticmethod
    def delete_message(db: Session, message_id: int, current_user_id: int):
        message = get_message(db, message_id)
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        participant = get_participant_by_user_and_conversation(db, current_user_id, message.conversation_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant in this conversation")
        if message.sender_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own messages")
        
        # Si es un mensaje de audio, eliminar el archivo usando FileStorageService
        if message.content_type == ContentType.AUDIO and message.media_url:
            file_service = FileStorageService()
            # Convertir la URL del audio a la ruta completa del archivo
            file_path = file_service.get_full_path_from_url(message.media_url)
            file_service.delete_audio_file(file_path)
            
        delete_message(db, message_id)
