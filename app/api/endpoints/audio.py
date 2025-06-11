from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.api.dependencies import get_current_user, get_db
from app.services.file_storage import FileStorageService
from app.crud import user as crud_user, message as crud_message, conversation as crud_conversation
from app.models.user import User
from app.websockets.manager import manager

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
        
        # Guardar el archivo y obtener la URL directamente
        audio_url = await file_service.save_audio_file(audio_file, current_user.id)
        
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
    """Servir archivos de audio de usuarios (audio de referencia)"""
    file_service = FileStorageService()
    file_path = os.path.join(file_service.user_audio_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )


@router.get("/user/{filename}")
async def get_user_audio_file(filename: str):
    """Servir archivos de audio de referencia de usuarios"""
    file_service = FileStorageService()
    file_path = os.path.join(file_service.user_audio_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        },
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


@router.post("/upload-message-audio")
async def upload_message_audio(
    audio_file: UploadFile = File(...),
    conversation_id: int = Form(...),
    content: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir audio para un mensaje en una conversación específica"""
    try:
        # Verificar que la conversación existe
        conversation = crud_conversation.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Verificar que el usuario es participante de la conversación
        user_is_participant = any(p.user_id == current_user.id for p in conversation.participants)
        if not user_is_participant:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta conversación")
        
        file_service = FileStorageService()
        
        # Guardar el archivo de audio del mensaje
        file_path = await file_service.save_message_audio_file(
            audio_file, 
            current_user.id, 
            conversation_id
        )
        
        # Generar URL para el archivo
        audio_url = file_service.get_message_file_url(file_path)
        
        # Crear el mensaje de audio en la base de datos
        audio_message = crud_message.create_audio_message(
            db=db,
            conversation_id=conversation_id,
            sender_id=current_user.id,
            media_url=audio_url,
            content=content
        )
        
        # Notificar via WebSocket a todos los participantes de la conversación
        await manager.send_to_conversation({
            "type": "new_message",
            "message": {
                "id": audio_message.id,
                "conversation_id": conversation_id,
                "sender_id": current_user.id,
                "content_type": "audio",
                "content": content or "",
                "media_url": audio_url,
                "created_at": audio_message.created_at.isoformat(),
                "is_read": False,
                "sender": {
                    "id": current_user.id,
                    "username": current_user.username
                }
            }
        }, str(conversation_id))
        
        return {
            "message": "Audio de mensaje subido exitosamente",
            "message_id": audio_message.id,
            "audio_url": audio_url,
            "conversation_id": conversation_id,
            "content_type": "audio"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/message/{filename}")
async def get_message_audio_file(filename: str):
    """Servir archivos de audio de mensajes"""
    file_service = FileStorageService()
    
    # Buscar el archivo en todos los subdirectorios de mensajes
    file_path = None
    for root, dirs, files in os.walk(file_service.message_audio_path):
        if filename in files:
            file_path = os.path.join(root, filename)
            break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )


@router.delete("/delete-message-audio/{message_id}")
async def delete_message_audio(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar audio de un mensaje específico"""
    try:
        # Verificar que el mensaje existe y pertenece al usuario
        message = crud_message.get_message(db, message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        if message.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este mensaje")
        
        if message.content_type.value != "audio":
            raise HTTPException(status_code=400, detail="El mensaje no es de tipo audio")
        
        # Eliminar el mensaje y su archivo
        success = crud_message.delete_audio_message(db, message_id)
        if not success:
            raise HTTPException(status_code=500, detail="Error al eliminar el mensaje de audio")
        
        return {"message": "Mensaje de audio eliminado exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
