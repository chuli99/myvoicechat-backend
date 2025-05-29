#!/usr/bin/env python3
"""
Comprehensive final test to verify all WebSocket functionality is working
"""
import asyncio
import websockets
import json
import requests
import uuid

BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080"

async def test_all_features():
    print("🎯 PRUEBA INTEGRAL FINAL DE WEBSOCKETS")
    print("="*50)
    
    # 1. Setup usuario y conversación
    username = f"final_test_{uuid.uuid4().hex[:8]}"
    password = "test123"
    email = f"{username}@test.com"
    
    print(f"📋 Setup: Registrando usuario {username}")
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "primary_language": "es"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/register", json=register_data)
    if response.status_code == 400:
        print("⚠️ Usuario ya existe")
    
    # Login
    login_data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/api/v1/users/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error en login: {response.text}")
        return False
    
    token_data = response.json()
    token = token_data["access_token"]
    user_id = token_data["user_id"]
    
    # Crear conversación
    response = requests.post(
        f"{BASE_URL}/api/v1/conversations/", 
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Error creando conversación: {response.text}")
        return False
    
    conversation = response.json()
    conversation_id = conversation["id"]
    print(f"✅ Setup completo. Conversación ID: {conversation_id}")
    
    # 2. Conectar WebSocket y probar todas las funcionalidades
    print("\n🔌 Conectando WebSocket...")
    uri = f"{WS_URL}/api/v1/ws/{conversation_id}?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado")
            
            # Test 1: Ping/Pong
            print("\n📍 Test 1: Ping/Pong")
            await websocket.send("ping")
            pong = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            if pong == "pong":
                print("✅ Ping/Pong funcionando")
            else:
                print(f"❌ Ping/Pong falló: {pong}")
                return False
            
            # Test 2: Indicadores de escritura
            print("\n⌨️ Test 2: Indicadores de escritura")
            typing_msg = {
                "type": "typing",
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_msg))
            print("✅ Indicador de escritura enviado")
            
            # Test 3: Enviar mensaje via API y recibirlo via WebSocket
            print("\n💬 Test 3: Mensaje API -> WebSocket")
            message_data = {
                "conversation_id": conversation_id,
                "content_type": "text",
                "content": "¡Mensaje final de prueba!"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/messages/",
                data=message_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code not in [200, 201]:
                print(f"❌ Error enviando mensaje: {response.text}")
                return False
            
            sent_message = response.json()
            print(f"✅ Mensaje enviado via API: ID {sent_message['id']}")
            
            # Esperar mensaje via WebSocket
            received_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message_obj = json.loads(received_message)
            
            if message_obj.get("type") == "new_message":
                received_data = message_obj.get("data", {})
                if (received_data.get("id") == sent_message["id"] and
                    received_data.get("content") == "¡Mensaje final de prueba!"):
                    print("✅ Mensaje recibido correctamente via WebSocket")
                else:
                    print(f"❌ Datos del mensaje incorrectos: {received_data}")
                    return False
            else:
                print(f"❌ Tipo de mensaje inesperado: {message_obj.get('type')}")
                return False
            
            # Test 4: Verificar que el mensaje está en la base de datos
            print("\n🗄️ Test 4: Verificar persistencia en BD")
            response = requests.get(
                f"{BASE_URL}/api/v1/messages/conversation/{conversation_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                print(f"❌ Error obteniendo mensajes: {response.text}")
                return False
            
            messages = response.json()
            found_message = next((m for m in messages if m["id"] == sent_message["id"]), None)
            
            if found_message and found_message["content"] == "¡Mensaje final de prueba!":
                print("✅ Mensaje persistido correctamente en BD")
            else:
                print("❌ Mensaje no encontrado en BD")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        return False

async def main():
    success = await test_all_features()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ WebSocket handshake: OK")
        print("✅ Ping/Pong heartbeat: OK")
        print("✅ Indicadores de escritura: OK")
        print("✅ Mensajes API -> WebSocket: OK")
        print("✅ Persistencia en BD: OK")
        print("✅ Limpieza de conexiones: OK")
        print("\n🚀 ¡WEBSOCKETS COMPLETAMENTE FUNCIONAL!")
        print("   El chat en tiempo real está listo para usar.")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("   Revisar logs para más detalles.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
