#!/usr/bin/env python3
"""
Script para probar WebSockets manualmente
"""
import asyncio
import websockets
import json

async def test_websocket():
    # Token de prueba (deberías usar un token real)
    token = "your-jwt-token-here"
    conversation_id = 1
    
    uri = f"ws://localhost:8080/api/v1/ws/{conversation_id}?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Conectado a {uri}")
            
            # Enviar ping
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"Ping response: {response}")
            
            # Enviar mensaje de typing
            typing_msg = {
                "type": "typing",
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_msg))
            print("Typing indicator sent")
            
            # Escuchar mensajes
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print(f"Mensaje recibido: {message}")
                except asyncio.TimeoutError:
                    print("Timeout - enviando ping...")
                    await websocket.send("ping")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Para probar WebSockets:")
    print("1. Asegúrate de que el servidor esté corriendo")
    print("2. Obtén un token JWT válido de tu aplicación")
    print("3. Reemplaza 'your-jwt-token-here' con el token real")
    print("4. Ejecuta: python test_websocket.py")
    
    # asyncio.run(test_websocket())
