from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.websockets.manager import manager
from app.api.dependencies import get_db
from app.services.participants_service import ParticipantsService
import logging
import json
import asyncio
from jose import JWTError, jwt
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def decode_websocket_token(token: str) -> dict:
    """Decode JWT token for WebSocket authentication"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_user_id_from_token(db: Session, token_payload: dict) -> int:
    """Get user_id from JWT token payload"""
    # The token contains username in 'sub' field, we need to get user_id
    username = token_payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    
    # Look up user by username to get user_id
    from app.crud.user import get_user_by_username
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    
    return user.id

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int, token: str = Query(...)):
    """WebSocket endpoint for real-time chat"""
    
    user_id = None
    conversation_id_str = str(conversation_id)
    
    try:
        # Accept WebSocket connection first
        await websocket.accept()
        
        # Get database session
        db = next(get_db())
        
        # Verify token
        try:
            payload = decode_websocket_token(token)
            user_id = get_user_id_from_token(db, payload)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            await websocket.close(code=4001)
            return
        
        # Verify user has access to conversation
        try:
            has_access = ParticipantsService.user_has_access_to_conversation(db, user_id, conversation_id)
            if not has_access:
                await websocket.close(code=4003)
                return
        except Exception as e:
            logger.error(f"Error verifying conversation access: {e}")
            await websocket.close(code=4011)
            return
        finally:
            db.close()
        
        # Register connection with manager
        await manager.connect(websocket, conversation_id_str, user_id)
        logger.info(f"User {user_id} successfully connected to conversation {conversation_id}")
        
        # Message loop
        while True:
            try:
                # Listen for client messages with timeout to prevent hanging
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                except asyncio.TimeoutError:
                    # Send ping to check if connection is alive
                    try:
                        await manager.send_personal_message("ping", websocket)
                        continue
                    except Exception:
                        logger.info(f"Connection timed out for user {user_id}")
                        break
                
                if data == "ping":
                    await manager.send_personal_message("pong", websocket)
                elif data.startswith("{"):
                    # Handle JSON messages (typing indicators, etc.)
                    try:
                        message_data = json.loads(data)
                        message_type = message_data.get("type")
                        
                        if message_type == "typing":
                            # Broadcast typing indicator to other users
                            await manager.broadcast_to_conversation({
                                "type": "typing",
                                "user_id": user_id,
                                "is_typing": message_data.get("is_typing", False)
                            }, conversation_id_str, exclude_user=user_id)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received from user {user_id}: {data}")
                        
            except WebSocketDisconnect:
                logger.info(f"User {user_id} disconnected normally from conversation {conversation_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop for user {user_id}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected during handshake")
    except Exception as e:
        logger.error(f"WebSocket connection error for user {user_id}: {e}")
    finally:
        # Clean up connection
        try:
            if user_id:
                disconnected_user = manager.disconnect(websocket, conversation_id_str)
                if disconnected_user:
                    await manager.broadcast_to_conversation({
                        "type": "user_left",
                        "user_id": disconnected_user,
                        "conversation_id": conversation_id
                    }, conversation_id_str)
        except Exception as e:
            logger.error(f"Error during WebSocket cleanup: {e}")
