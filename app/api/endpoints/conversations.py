from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.crud import conversation as crud_conversation
from app.services.conversations_service import ConversationsService
from app.schemas import (
    Conversation, ConversationCreate, ConversationDetail,
    ParticipantCreate, User as UserSchema
)
from app.schemas.conversation import ConversationSummary

router = APIRouter()


@router.post("/", response_model=Conversation)
def create_new_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation and add the current user as a participant"""
    conversation = ConversationsService.create_new_conversation(db, current_user.id)
    return conversation


@router.get("/", response_model=List[Conversation])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    conversations = ConversationsService.read_conversations(db, current_user.id)
    return conversations


@router.get("/all", response_model=List[ConversationSummary])
def get_all_conversations(
    skip: int = Query(0, ge=0, description="Número de conversaciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de conversaciones a retornar"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las conversaciones creadas en el sistema.
    Requiere autenticación. Solo usuarios autenticados pueden acceder.
    """
    try:
        # Obtener todas las conversaciones
        conversations = crud_conversation.get_all_conversations(
            db=db, 
            skip=skip, 
            limit=limit
        )
        
        # Crear respuesta con información adicional
        result = []
        for conv in conversations:
            # Contar participantes
            participant_count = len(conv.participants) if conv.participants else 0
            
            # Contar mensajes
            message_count = len(conv.messages) if conv.messages else 0
            
            conv_summary = ConversationSummary(
                id=conv.id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                participant_count=participant_count,
                message_count=message_count
            )
            result.append(conv_summary)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener todas las conversaciones: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation with its participants and messages"""
    conversation = ConversationsService.read_conversation(db, conversation_id, current_user.id)
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    ConversationsService.delete_conversation(db, conversation_id, current_user.id)
