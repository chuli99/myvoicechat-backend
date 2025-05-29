#!/usr/bin/env python3

import asyncio
import websockets
import json
import sys

async def test_websocket():
    # Replace with actual values
    conversation_id = 1
    token = "your_jwt_token_here"  # You'll need to get this from login
    
    uri = f"ws://localhost:8080/api/v1/ws/{conversation_id}?token={token}"
    
    try:
        print(f"🔌 Conectando a: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Conexión WebSocket establecida")
            
            # Send a ping
            await websocket.send("ping")
            print("📤 Ping enviado")
            
            # Wait for pong
            response = await websocket.recv()
            print(f"📥 Respuesta recibida: {response}")
            
            # Send typing indicator
            typing_message = {
                "type": "typing",
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_message))
            print("📤 Indicador de escritura enviado")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Stop typing
            typing_message["is_typing"] = False
            await websocket.send(json.dumps(typing_message))
            print("📤 Indicador de escritura detenido")
            
            print("✅ Test completado exitosamente")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Conexión cerrada: {e.code} - {e.reason}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Código de estado inválido: {e.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Test de WebSocket")
    print("Nota: Necesitas un token JWT válido para probar")
    print("Puedes obtenerlo haciendo login en la aplicación")
    
    # Check if token is provided as argument
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"Token proporcionado: {token[:20]}...")
    
    asyncio.run(test_websocket())
