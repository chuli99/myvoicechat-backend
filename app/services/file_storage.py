import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import aiofiles


class FileStorageService:
    def __init__(self, base_path: str = "uploads/audio"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    async def save_audio_file(self, file: UploadFile, user_id: int) -> str:
        """
        Guarda el archivo de audio y retorna la ruta completa del archivo
        """
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser de audio")
        
        # Validar tamaño del archivo (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")
        
        # Generar nombre único
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'wav'
        unique_filename = f"user_{user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(self.base_path, unique_filename)
        
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
        # Extraer solo el nombre del archivo de la ruta completa
        filename = os.path.basename(file_path)
        return f"/api/audio/{filename}"
    
    def get_full_path_from_url(self, audio_url: str) -> str:
        """Convierte una URL de audio de vuelta a la ruta completa del archivo"""
        filename = audio_url.split('/')[-1]
        return os.path.join(self.base_path, filename)
