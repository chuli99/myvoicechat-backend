from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.api.dependencies import get_current_user, get_db
from app.services.file_storage import FileStorageService
from app.crud import user as crud_user
from app.models.user import User

router = APIRouter()


@router.post("/upload-reference-audio")
async def upload_reference_audio(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir audio de referencia para el usuario"""
    try:
        file_service = FileStorageService()
        
        # Guardar el archivo
        file_path = await file_service.save_audio_file(audio_file, current_user.id)
        
        # Generar URL para el archivo
        audio_url = file_service.get_file_url(file_path)
        
        # Actualizar usuario en la base de datos
        updated_user = crud_user.update_user_audio(
            db=db,
            user_id=current_user.id,
            audio_url=audio_url
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "message": "Audio subido exitosamente",
            "audio_url": audio_url
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Servir archivos de audio"""
    file_service = FileStorageService()
    file_path = os.path.join(file_service.base_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )


@router.delete("/delete-reference-audio")
async def delete_reference_audio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar audio de referencia del usuario"""
    try:
        if not current_user.ref_audio_url:
            raise HTTPException(status_code=404, detail="El usuario no tiene audio de referencia")
        
        file_service = FileStorageService()
        file_path = file_service.get_full_path_from_url(current_user.ref_audio_url)
        
        # Eliminar archivo del sistema
        file_service.delete_audio_file(file_path)
        
        # Actualizar usuario en la base de datos
        updated_user = crud_user.update_user_audio(
            db=db,
            user_id=current_user.id,
            audio_url=None
        )
        
        return {"message": "Audio de referencia eliminado exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
