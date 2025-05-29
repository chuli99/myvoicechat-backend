#!/usr/bin/env python3
"""
Test script to verify the WebSocket-enabled frontend functionality
"""
import asyncio
import websockets
import json
import requests
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080"

async def test_frontend_websocket():
    print("🧪 Probando funcionalidad WebSocket del frontend...")
    
    # 1. Registrar/autenticar usuario
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "test123"
    email = f"{username}@test.com"
    
    print(f"1️⃣ Registrando usuario: {username}")
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "primary_language": "es"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/register", json=register_data)
    if response.status_code == 400 and "already registered" in response.text:
        print("⚠️ Usuario ya existe, continuando...")
    elif response.status_code not in [200, 201]:
        print(f"❌ Error registrando usuario: {response.status_code} - {response.text}")
        return False
    
    # 2. Login
    print("2️⃣ Iniciando sesión...")
    login_data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/api/v1/users/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return False
    
    token_data = response.json()
    token = token_data["access_token"]
    user_id = token_data["user_id"]
    print(f"✅ Login exitoso. User ID: {user_id}")
    
    # 3. Crear conversación
    print("3️⃣ Creando conversación...")
    conversation_data = {}
    response = requests.post(
        f"{BASE_URL}/api/v1/conversations/", 
        json=conversation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Error creando conversación: {response.status_code} - {response.text}")
        return False
    
    conversation = response.json()
    conversation_id = conversation["id"]
    print(f"✅ Conversación creada: ID {conversation_id}")
    
    # 4. Conectar WebSocket (simulando frontend)
    print("4️⃣ Conectando WebSocket...")
    uri = f"{WS_URL}/api/v1/ws/{conversation_id}?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado")
            
            # 5. Enviar mensaje via API (como lo haría el frontend)
            print("5️⃣ Enviando mensaje via API...")
            message_data = {
                "conversation_id": conversation_id,
                "content_type": "text",
                "content": "Mensaje de prueba frontend WebSocket"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/messages/",
                data=message_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
                return False
            
            message = response.json()
            print(f"✅ Mensaje enviado via API: ID {message['id']}")
            
            # 6. Esperar mensaje via WebSocket
            print("6️⃣ Esperando mensaje via WebSocket...")
            try:
                message_data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                message_obj = json.loads(message_data)
                
                if message_obj.get("type") == "new_message":
                    print(f"✅ Mensaje recibido via WebSocket: {message_obj}")
                    
                    # Verificar datos del mensaje
                    msg_data = message_obj.get("data", {})
                    if (msg_data.get("content") == "Mensaje de prueba frontend WebSocket" and
                        msg_data.get("sender_id") == user_id and
                        msg_data.get("conversation_id") == conversation_id):
                        print("✅ Datos del mensaje correctos")
                        return True
                    else:
                        print(f"❌ Datos del mensaje incorrectos: {msg_data}")
                        return False
                else:
                    print(f"❌ Tipo de mensaje inesperado: {message_obj.get('type')}")
                    return False
                    
            except asyncio.TimeoutError:
                print("❌ Timeout esperando mensaje WebSocket")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando WebSocket: {e}")
        return False

async def main():
    success = await test_frontend_websocket()
    
    if success:
        print("\n" + "="*50)
        print("🎉 ¡PRUEBA FRONTEND WEBSOCKET EXITOSA!")
        print("✅ El frontend puede enviar mensajes via API")
        print("✅ El frontend puede recibir mensajes via WebSocket")
        print("✅ Los datos se transmiten correctamente")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ PRUEBA FRONTEND WEBSOCKET FALLÓ")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
