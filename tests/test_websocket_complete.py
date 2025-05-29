#!/usr/bin/env python3

import asyncio
import aiohttp
import websockets
import json
import sys

BASE_URL = "http://localhost:8080"
WS_BASE_URL = "ws://localhost:8080"

async def test_full_websocket_flow():
    """Test the complete WebSocket flow: register, login, create conversation, connect WebSocket"""
    
    print("🧪 Iniciando test completo de WebSocket...")
    
    session = aiohttp.ClientSession()
    
    try:
        # Step 1: Register a test user
        print("\n1️⃣ Registrando usuario de prueba...")
        register_data = {
            "username": "websocket_test_user",
            "email": "wstest@example.com",
            "password": "testpass123"
        }
        
        async with session.post(f"{BASE_URL}/api/v1/users/register", json=register_data) as resp:
            if resp.status == 200:
                user_data = await resp.json()
                print(f"✅ Usuario registrado: {user_data['username']}")
            elif resp.status == 400:
                print("⚠️ Usuario ya existe, continuando...")
            else:
                print(f"❌ Error al registrar: {resp.status}")
                return False
        
        # Step 2: Login
        print("\n2️⃣ Iniciando sesión...")
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        
        async with session.post(f"{BASE_URL}/api/v1/users/login", json=login_data) as resp:
            if resp.status == 200:
                login_response = await resp.json()
                token = login_response["access_token"]
                user_id = login_response["user_id"]
                print(f"✅ Login exitoso. User ID: {user_id}")
            else:
                print(f"❌ Error al hacer login: {resp.status}")
                error_text = await resp.text()
                print(f"Error details: {error_text}")
                return False
        
        # Step 3: Create a conversation
        print("\n3️⃣ Creando conversación...")
        headers = {"Authorization": f"Bearer {token}"}
        conv_data = {"name": "WebSocket Test Conversation"}
        
        async with session.post(f"{BASE_URL}/api/v1/conversations/", json=conv_data, headers=headers) as resp:
            if resp.status == 200:
                conversation = await resp.json()
                conversation_id = conversation["id"]
                print(f"✅ Conversación creada: ID {conversation_id}")
            else:
                print(f"❌ Error al crear conversación: {resp.status}")
                return False
        
        # Step 4: Test WebSocket connection
        print("\n4️⃣ Probando conexión WebSocket...")
        ws_url = f"{WS_BASE_URL}/api/v1/ws/{conversation_id}?token={token}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ Conexión WebSocket establecida")
                
                # Test ping/pong
                print("📤 Enviando ping...")
                await websocket.send("ping")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                if response == "pong":
                    print("✅ Pong recibido correctamente")
                else:
                    print(f"⚠️ Respuesta inesperada: {response}")
                
                # Test typing indicator
                print("📤 Enviando indicador de escritura...")
                typing_msg = {"type": "typing", "is_typing": True}
                await websocket.send(json.dumps(typing_msg))
                
                # Wait a bit and stop typing
                await asyncio.sleep(1)
                typing_msg["is_typing"] = False
                await websocket.send(json.dumps(typing_msg))
                print("✅ Indicadores de escritura enviados")
                
                print("✅ Test de WebSocket completado exitosamente")
                return True
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Conexión WebSocket cerrada: {e.code} - {e.reason}")
            return False
        except asyncio.TimeoutError:
            print("❌ Timeout esperando respuesta WebSocket")
            return False
        except Exception as e:
            print(f"❌ Error en WebSocket: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        await session.close()

async def test_websocket_with_existing_data():
    """Test WebSocket with existing conversation and token"""
    
    print("🧪 Test simple de WebSocket (requiere datos existentes)...")
    
    # You can manually set these values if you have them
    conversation_id = 1
    token = None  # Set manually if you have a valid token
    
    if not token:
        print("❌ Token no proporcionado. Usa: python test_websocket_manual.py <token>")
        return False
    
    ws_url = f"{WS_BASE_URL}/api/v1/ws/{conversation_id}?token={token}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Conexión WebSocket establecida")
            
            # Test ping/pong
            await websocket.send("ping")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Respuesta: {response}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If token provided, use simple test
        token = sys.argv[1]
        async def test_with_token():
            conversation_id = 1
            ws_url = f"{WS_BASE_URL}/api/v1/ws/{conversation_id}?token={token}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    print("✅ Conexión WebSocket establecida")
                    await websocket.send("ping")
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📥 Respuesta: {response}")
                    return True
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        
        asyncio.run(test_with_token())
    else:
        # Full test
        success = asyncio.run(test_full_websocket_flow())
        sys.exit(0 if success else 1)
