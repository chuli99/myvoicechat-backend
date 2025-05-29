from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # conversation_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, conversation_id: str, user_id: int):
        """Connect a websocket to a conversation"""
        # Don't accept here - should already be accepted in endpoint
        
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        
        # Store websocket with user info
        websocket.user_id = user_id
        self.active_connections[conversation_id].append(websocket)
        
        logger.info(f"User {user_id} connected to conversation {conversation_id}")
        
        # Notify other participants that user joined
        await self.broadcast_to_conversation({
            "type": "user_joined",
            "user_id": user_id,
            "conversation_id": conversation_id
        }, conversation_id, exclude_user=user_id)
    
    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Disconnect a websocket from a conversation"""
        if conversation_id in self.active_connections:
            try:
                user_id = getattr(websocket, 'user_id', None)
                self.active_connections[conversation_id].remove(websocket)
                
                logger.info(f"User {user_id} disconnected from conversation {conversation_id}")
                
                # Clean up empty conversation lists
                if not self.active_connections[conversation_id]:
                    del self.active_connections[conversation_id]
                
                return user_id
            except ValueError:
                pass  # Websocket was not in the list
        return None
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific websocket"""
        try:
            if hasattr(websocket, 'client_state') and websocket.client_state.value == 1:  # CONNECTED
                await websocket.send_text(message)
            elif hasattr(websocket, 'application_state') and websocket.application_state.value == 2:  # CONNECTED
                await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Remove dead connection
            for conv_id, connections in self.active_connections.items():
                if websocket in connections:
                    self.disconnect(websocket, conv_id)
                    break
    
    async def broadcast_to_conversation(self, message: dict, conversation_id: str, exclude_user: int = None):
        """Broadcast a message to all connections in a conversation"""
        if conversation_id not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        dead_connections = []
        
        for connection in self.active_connections[conversation_id]:
            # Skip if this is the user we want to exclude
            if exclude_user and getattr(connection, 'user_id', None) == exclude_user:
                continue
                
            try:
                # Check connection state more carefully
                is_connected = False
                if hasattr(connection, 'client_state') and connection.client_state.value == 1:
                    is_connected = True
                elif hasattr(connection, 'application_state') and connection.application_state.value == 2:
                    is_connected = True
                    
                if is_connected:
                    await connection.send_text(message_str)
                else:
                    dead_connections.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, conversation_id)
    
    async def send_to_conversation(self, message: dict, conversation_id: str):
        """Send a message to all connections in a conversation (including sender)"""
        if conversation_id not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        dead_connections = []
        
        for connection in self.active_connections[conversation_id]:
            try:
                # Check connection state more carefully
                is_connected = False
                if hasattr(connection, 'client_state') and connection.client_state.value == 1:
                    is_connected = True
                elif hasattr(connection, 'application_state') and connection.application_state.value == 2:
                    is_connected = True
                    
                if is_connected:
                    await connection.send_text(message_str)
                else:
                    dead_connections.append(connection)
            except Exception as e:
                logger.error(f"Error sending message to conversation: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, conversation_id)
    
    def get_conversation_users(self, conversation_id: str) -> List[int]:
        """Get list of user IDs connected to a conversation"""
        if conversation_id not in self.active_connections:
            return []
        
        return [getattr(conn, 'user_id', None) for conn in self.active_connections[conversation_id] 
                if hasattr(conn, 'user_id')]
    
    def is_user_online(self, conversation_id: str, user_id: int) -> bool:
        """Check if a user is online in a conversation"""
        if conversation_id not in self.active_connections:
            return False
        
        for conn in self.active_connections[conversation_id]:
            if getattr(conn, 'user_id', None) == user_id:
                return True
        return False

# Global instance
manager = ConnectionManager()
