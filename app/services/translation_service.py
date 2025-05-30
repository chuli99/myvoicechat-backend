import httpx
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.participant import Participant
from app.models.user import User
from app.crud.translated_message import translated_message_crud
from app.schemas.translated_message import TranslatedMessageCreate, TranslateRequest
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    TRANSLATION_API_URL = "http://127.0.0.1:8000/translate/"
    
    @staticmethod
    async def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Call the translation API"""
        translate_request = TranslateRequest(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TranslationService.TRANSLATION_API_URL,
                    json=translate_request.dict(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("translated_text")
                
        except httpx.RequestError as e:
            logger.error(f"Translation API request failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Translation API returned error status {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during translation: {e}")
            return None
    
    @staticmethod
    def get_other_participant_language(db: Session, conversation_id: int, sender_id: int) -> Optional[str]:
        """Get the primary language of the other participant in the conversation"""
        # Get all participants in the conversation except the sender
        other_participant = db.query(Participant).join(User).filter(
            Participant.conversation_id == conversation_id,
            Participant.user_id != sender_id
        ).first()
        
        if other_participant and other_participant.user:
            return other_participant.user.primary_language
        
        return None
    
    @staticmethod
    async def create_translated_message(db: Session, message: Message) -> Optional[int]:
        """Create a translated message for the given original message"""
        if not message.content or not message.sender:
            logger.warning(f"Message {message.id} has no content or sender, skipping translation")
            return None
        
        # Get sender's primary language
        sender_language = message.sender.primary_language
        if not sender_language:
            logger.warning(f"Sender {message.sender_id} has no primary language set, skipping translation")
            return None
        
        # Get the other participant's language
        target_language = TranslationService.get_other_participant_language(
            db, message.conversation_id, message.sender_id
        )
        
        if not target_language:
            logger.warning(f"Could not find target language for conversation {message.conversation_id}, skipping translation")
            return None
        
        # Skip translation if source and target languages are the same
        if sender_language == target_language:
            logger.info(f"Source and target languages are the same ({sender_language}), skipping translation")
            return None
        
        # Translate the content
        translated_content = await TranslationService.translate_text(
            message.content, sender_language, target_language
        )
        
        if not translated_content:
            logger.error(f"Failed to translate message {message.id}")
            return None
        
        # Create the translated message record
        translated_message_data = TranslatedMessageCreate(
            original_message_id=message.id,
            target_language=target_language,
            translated_content=translated_content
        )
        
        try:
            translated_message = translated_message_crud.create(db, translated_message_data)
            logger.info(f"Created translated message {translated_message.id} for original message {message.id}")
            return translated_message.id
        except Exception as e:
            logger.error(f"Failed to create translated message for message {message.id}: {e}")
            return None
