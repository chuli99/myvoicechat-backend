import httpx
import os
import aiofiles
from sqlalchemy.orm import Session
from app.models.message import Message, ContentType
from app.models.participant import Participant
from app.models.user import User
from app.crud.translated_message import translated_message_crud
from app.schemas.translated_message import TranslatedMessageCreate, TranslateRequest
from app.services.file_storage import FileStorageService
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    TRANSLATION_API_URL = "http://127.0.0.1:8000/translate/"
    AUDIO_TRANSLATION_API_URL = "http://localhost:8000/translate-audio/"
    
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
    async def translate_audio(audio_file_path: str, source_lang: str, target_lang: str, voice_reference_path: str, model: str = "F5TTS_v1_Base") -> Optional[bytes]:
        """Call the audio translation API"""
        try:
            async with httpx.AsyncClient() as client:
                # Preparar los archivos para multipart/form-data
                with open(audio_file_path, 'rb') as audio_file, open(voice_reference_path, 'rb') as voice_file:
                    files = {
                        'audio_file': ('audio.wav', audio_file, 'audio/wav'),
                        'voice_reference_file': ('voice_ref.wav', voice_file, 'audio/wav')
                    }
                    data = {
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'model': model
                    }
                    
                    response = await client.post(
                        TranslationService.AUDIO_TRANSLATION_API_URL,
                        files=files,
                        data=data,
                        timeout=60.0  # Timeout más largo para audio
                    )
                    response.raise_for_status()
                    
                    return response.content
                    
        except httpx.RequestError as e:
            logger.error(f"Audio translation API request failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Audio translation API returned error status {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during audio translation: {e}")
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
        """Create a translated message for the given original message (text or audio)"""
        if not message.sender:
            logger.warning(f"Message {message.id} has no sender, skipping translation")
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
        
        if message.content_type == ContentType.TEXT:
            return await TranslationService._create_text_translation(db, message, sender_language, target_language)
        elif message.content_type == ContentType.AUDIO:
            return await TranslationService._create_audio_translation(db, message, sender_language, target_language)
        else:
            logger.warning(f"Unsupported content type {message.content_type} for message {message.id}")
            return None
    
    @staticmethod
    async def _create_text_translation(db: Session, message: Message, sender_language: str, target_language: str) -> Optional[int]:
        """Create a translated message for text content"""
        if not message.content:
            logger.warning(f"Text message {message.id} has no content, skipping translation")
            return None
        
        # Translate the content
        translated_content = await TranslationService.translate_text(
            message.content, sender_language, target_language
        )
        
        if not translated_content:
            logger.error(f"Failed to translate text message {message.id}")
            return None
        
        # Create the translated message record
        translated_message_data = TranslatedMessageCreate(
            original_message_id=message.id,
            target_language=target_language,
            translated_content=translated_content,
            content_type="TEXT"
        )
        
        try:
            translated_message = translated_message_crud.create(db, translated_message_data)
            logger.info(f"Created translated text message {translated_message.id} for original message {message.id}")
            return translated_message.id
        except Exception as e:
            logger.error(f"Failed to create translated text message for message {message.id}: {e}")
            return None
    
    @staticmethod
    async def _create_audio_translation(db: Session, message: Message, sender_language: str, target_language: str) -> Optional[int]:
        """Create a translated message for audio content"""
        if not message.media_url:
            logger.warning(f"Audio message {message.id} has no media_url, skipping translation")
            return None
        
        # Get the sender's voice reference audio (for voice cloning)
        if not message.sender.ref_audio_url:
            logger.warning(f"Sender {message.sender_id} has no ref_audio_url, skipping audio translation")
            return None
        
        # Convert URLs to file paths
        file_service = FileStorageService()
        audio_file_path = file_service.get_full_path_from_url(message.media_url)
        voice_reference_path = file_service.get_full_path_from_url(message.sender.ref_audio_url)
        
        logger.info(f"Message media_url: {message.media_url}")
        logger.info(f"Sender ref_audio_url: {message.sender.ref_audio_url}")
        logger.info(f"Resolved audio_file_path: {audio_file_path}")
        logger.info(f"Resolved voice_reference_path: {voice_reference_path}")
        
        # Verificar que los archivos existen
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return None
        
        if not os.path.exists(voice_reference_path):
            logger.error(f"Voice reference file not found: {voice_reference_path}")
            return None
        
        logger.info(f"Translating audio from {sender_language} to {target_language}")
        logger.info(f"Audio file: {audio_file_path}")
        logger.info(f"Voice reference file: {voice_reference_path}")
        
        # Translate the audio
        translated_audio_bytes = await TranslationService.translate_audio(
            audio_file_path, sender_language, target_language, voice_reference_path
        )
        
        if not translated_audio_bytes:
            logger.error(f"Failed to translate audio message {message.id}")
            return None
        
        # Save the translated audio file
        try:
            # Crear directorio para audios clonados si no existe
            clone_audio_dir = "uploads/audio/message_clon"
            os.makedirs(clone_audio_dir, exist_ok=True)
            
            # Generar nombre único para el archivo traducido
            import uuid
            translated_filename = f"translated_{message.id}_{target_language}_{uuid.uuid4().hex}.wav"
            translated_file_path = os.path.join(clone_audio_dir, translated_filename)
            
            # Guardar el archivo de audio traducido
            async with aiofiles.open(translated_file_path, 'wb') as f:
                await f.write(translated_audio_bytes)
            
            # Generar URL para el archivo traducido
            translated_media_url = f"/api/uploads/audio/message_clon/{translated_filename}"
            
            # Create the translated message record
            translated_message_data = TranslatedMessageCreate(
                original_message_id=message.id,
                target_language=target_language,
                media_url=translated_media_url,
                content_type="AUDIO"
            )
            
            translated_message = translated_message_crud.create(db, translated_message_data)
            logger.info(f"Created translated audio message {translated_message.id} for original message {message.id}")
            return translated_message.id
            
        except Exception as e:
            logger.error(f"Failed to save translated audio or create translated message for message {message.id}: {e}")
            return None
