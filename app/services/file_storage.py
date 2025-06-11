import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import aiofiles


class FileStorageService:
    def __init__(self, base_path: str = "uploads/audio"):
        self.base_path = base_path
        self.user_audio_path = os.path.join(base_path, "users")
        self.message_audio_path = os.path.join(base_path, "messages")
        
        # Crear directorios si no existen
        os.makedirs(self.user_audio_path, exist_ok=True)
        os.makedirs(self.message_audio_path, exist_ok=True)
    
    async def save_audio_file(self, file: UploadFile, user_id: int) -> str:
        """
        Guarda el archivo de audio de referencia del usuario y retorna la URL para ref_audio_url
        """
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser de audio")
        
        # Validar tamaño del archivo (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")
        
        # Generar nombre único para audio de usuario
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'wav'
        unique_filename = f"user_{user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(self.user_audio_path, unique_filename)
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Retornar la URL que se guardará en ref_audio_url
        return f"/api/v1/audio/user/{unique_filename}"
    
    async def save_message_audio_file(self, file: UploadFile, user_id: int, conversation_id: int) -> str:
        """
        Guarda el archivo de audio de un mensaje y retorna la ruta completa del archivo
        """
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser de audio")
        
        # Validar tamaño del archivo (max 25MB para mensajes de audio)
        max_size = 25 * 1024 * 1024  # 25MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="El archivo de audio es demasiado grande (máximo 25MB)")
        
        # Crear subdirectorio por conversación para mejor organización
        conversation_dir = os.path.join(self.message_audio_path, f"conv_{conversation_id}")
        os.makedirs(conversation_dir, exist_ok=True)
        
        # Generar nombre único para audio de mensaje
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'wav'
        unique_filename = f"msg_{user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(conversation_dir, unique_filename)
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path
    
    def delete_audio_file(self, file_path: str) -> bool:
        """Elimina un archivo de audio dado su ruta completa"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    def get_file_url(self, file_path: str) -> str:
        """Convierte la ruta del archivo a URL para el API"""
        # Extraer el nombre del archivo y determinar el tipo
        filename = os.path.basename(file_path)
        
        # Determinar si es un archivo de usuario o mensaje basado en la ruta
        if "/users/" in file_path:
            return f"/api/v1/audio/user/{filename}"
        elif "/messages/" in file_path:
            return f"/api/v1/audio/message/{filename}"
        else:
            # Fallback para compatibilidad con archivos existentes
            return f"/api/v1/audio/user/{filename}"
    
    def get_message_file_url(self, file_path: str) -> str:
        """Convierte la ruta del archivo de mensaje a URL específica para mensajes"""
        filename = os.path.basename(file_path)
        return f"/api/v1/audio/message/{filename}"
    
    def get_full_path_from_url(self, audio_url: str) -> str:
        """Convierte una URL de audio de vuelta a la ruta completa del archivo"""
        filename = audio_url.split('/')[-1]
        
        # Determinar si es un archivo de usuario o mensaje basado en la URL
        if "/message/" in audio_url:
            # Para mensajes, buscar en todos los subdirectorios de conversaciones
            for root, dirs, files in os.walk(self.message_audio_path):
                if filename in files:
                    return os.path.join(root, filename)
            return os.path.join(self.message_audio_path, filename)
        elif "/user/" in audio_url:
            # Para usuarios, buscar en el directorio de usuarios
            return os.path.join(self.user_audio_path, filename)
        else:
            # Fallback para compatibilidad - asumir que es de usuario
            return os.path.join(self.user_audio_path, filename)
