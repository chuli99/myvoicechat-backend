#!/usr/bin/env python3

import asyncio
import aiohttp
import websockets
import json

BASE_URL = "http://localhost:8080"
WS_BASE_URL = "ws://localhost:8080"

async def test_real_time_messaging():
    """Test real-time messaging via WebSocket"""
    
    print("💬 Probando mensajes en tiempo real...")
    
    session = aiohttp.ClientSession()
    
    try:
        # Login to get token
        print("🔑 Haciendo login...")
        login_data = {"username": "websocket_test_user", "password": "testpass123"}
        async with session.post(f"{BASE_URL}/api/v1/users/login", json=login_data) as resp:
            if resp.status != 200:
                print(f"❌ Error en login: {resp.status}")
                return False
            
            login_response = await resp.json()
            token = login_response["access_token"]
            user_id = login_response["user_id"]
            print(f"✅ Login exitoso. User ID: {user_id}")
        
        # Create conversation
        print("📝 Creando conversación...")
        headers = {"Authorization": f"Bearer {token}"}
        conv_data = {"name": "Real-time Test Conversation"}
        
        async with session.post(f"{BASE_URL}/api/v1/conversations/", json=conv_data, headers=headers) as resp:
            if resp.status != 200:
                print(f"❌ Error creando conversación: {resp.status}")
                return False
                
            conversation = await resp.json()
            conversation_id = conversation["id"]
            print(f"✅ Conversación creada: ID {conversation_id}")
        
        # Connect to WebSocket
        ws_url = f"{WS_BASE_URL}/api/v1/ws/{conversation_id}?token={token}"
        print(f"🔌 Conectando a WebSocket...")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket conectado")
            
            # Send a test message via HTTP API
            print("📤 Enviando mensaje via API...")
            
            # Prepare to listen for WebSocket message
            async def listen_for_message():
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        if message != "pong":  # Ignore pong responses
                            return json.loads(message)
                except asyncio.TimeoutError:
                    return None
            
            # Start listening task
            listen_task = asyncio.create_task(listen_for_message())
            
            # Send message via API
            form_data = aiohttp.FormData()
            form_data.add_field('conversation_id', str(conversation_id))
            form_data.add_field('content_type', 'text')
            form_data.add_field('content', 'Hello from WebSocket test!')
            
            async with session.post(f"{BASE_URL}/api/v1/messages/", data=form_data, headers=headers) as resp:
                if resp.status == 200:
                    message_response = await resp.json()
                    print(f"✅ Mensaje enviado via API: ID {message_response['id']}")
                else:
                    print(f"❌ Error enviando mensaje: {resp.status}")
                    return False
            
            # Wait for WebSocket message
            print("👂 Esperando mensaje via WebSocket...")
            websocket_message = await listen_task
            
            if websocket_message:
                print(f"✅ Mensaje recibido via WebSocket: {websocket_message}")
                
                # Verify it's the correct message
                if (websocket_message.get('type') == 'new_message' and 
                    websocket_message.get('data', {}).get('content') == 'Hello from WebSocket test!'):
                    print("🎉 ¡Mensajería en tiempo real funcionando perfectamente!")
                    return True
                else:
                    print(f"⚠️ Mensaje recibido pero contenido inesperado: {websocket_message}")
                    return False
            else:
                print("❌ No se recibió mensaje via WebSocket (timeout)")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await session.close()

if __name__ == "__main__":
    success = asyncio.run(test_real_time_messaging())
    print("\n" + "="*50)
    if success:
        print("🎉 ¡TODOS LOS TESTS PASARON! WebSocket está funcionando correctamente.")
    else:
        print("❌ Algunos tests fallaron. Revisar logs.")
    print("="*50)
