#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de traducción automática de audio
"""
import asyncio
import httpx
import json
import os
from pathlib import Path

# Configuración de la API
BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"

async def test_audio_translation_workflow():
    """
    Test completo del flujo de traducción de audio:
    1. Crear dos usuarios con diferentes idiomas y archivos de voz de referencia
    2. Crear una conversación entre ellos
    3. Enviar un mensaje de audio
    4. Verificar que se crea automáticamente la traducción de audio
    """
    async with httpx.AsyncClient() as client:
        
        print("🎵 Iniciando test de traducción automática de audio...")
        
        # 1. Crear usuario 1 (español)
        user1_data = {
            "username": "maria_es",
            "email": "maria@test.com",
            "password": "password123",
            "primary_language": "es"
        }
        
        print("\n📝 Creando usuario 1 (español)...")
        response = await client.post(f"{API_BASE_URL}/auth/register", json=user1_data)
        if response.status_code != 201:
            print(f"❌ Error creando usuario 1: {response.status_code} - {response.text}")
            return
        user1 = response.json()
        print(f"✅ Usuario 1 creado: {user1['username']} (ID: {user1['id']})")
        
        # 2. Crear usuario 2 (inglés)
        user2_data = {
            "username": "john_en",
            "email": "john@test.com", 
            "password": "password123",
            "primary_language": "en"
        }
        
        print("\n📝 Creando usuario 2 (inglés)...")
        response = await client.post(f"{API_BASE_URL}/auth/register", json=user2_data)
        if response.status_code != 201:
            print(f"❌ Error creando usuario 2: {response.status_code} - {response.text}")
            return
        user2 = response.json()
        print(f"✅ Usuario 2 creado: {user2['username']} (ID: {user2['id']})")
        
        # 3. Login usuario 1
        print("\n🔐 Haciendo login con usuario 1...")
        login_data = {"username": "maria_es", "password": "password123"}
        response = await client.post(f"{API_BASE_URL}/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Error en login usuario 1: {response.status_code} - {response.text}")
            return
        
        token_data = response.json()
        headers1 = {"Authorization": f"Bearer {token_data['access_token']}"}
        print("✅ Login exitoso para usuario 1")
        
        # 4. Login usuario 2
        print("\n🔐 Haciendo login con usuario 2...")
        login_data = {"username": "john_en", "password": "password123"}
        response = await client.post(f"{API_BASE_URL}/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Error en login usuario 2: {response.status_code} - {response.text}")
            return
        
        token_data = response.json()
        headers2 = {"Authorization": f"Bearer {token_data['access_token']}"}
        print("✅ Login exitoso para usuario 2")
        
        # 5. Verificar que tenemos archivos de audio de prueba
        test_audio_path = Path("uploads/audio/334faa64-ee54-4d68-87f7-1a4fd2e76424.wav")
        if not test_audio_path.exists():
            print(f"❌ No se encontró archivo de audio de prueba en {test_audio_path}")
            print("💡 Asegúrate de tener un archivo de audio de prueba disponible")
            return
        
        print(f"✅ Archivo de audio de prueba encontrado: {test_audio_path}")
        
        # 6. Subir archivo de voz de referencia para usuario 1
        print("\n🎤 Subiendo archivo de voz de referencia para usuario 1...")
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio_file': ('voice_ref_maria.wav', audio_file, 'audio/wav')}
            response = await client.post(
                f"{API_BASE_URL}/users/upload-reference-audio", 
                files=files, 
                headers=headers1
            )
        
        if response.status_code != 200:
            print(f"❌ Error subiendo voz de referencia usuario 1: {response.status_code} - {response.text}")
            return
        print("✅ Voz de referencia subida para usuario 1")
        
        # 7. Subir archivo de voz de referencia para usuario 2
        print("\n🎤 Subiendo archivo de voz de referencia para usuario 2...")
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio_file': ('voice_ref_john.wav', audio_file, 'audio/wav')}
            response = await client.post(
                f"{API_BASE_URL}/users/upload-reference-audio", 
                files=files, 
                headers=headers2
            )
        
        if response.status_code != 200:
            print(f"❌ Error subiendo voz de referencia usuario 2: {response.status_code} - {response.text}")
            return
        print("✅ Voz de referencia subida para usuario 2")
        
        # 8. Crear conversación
        print("\n💬 Creando conversación...")
        conversation_data = {
            "participant_ids": [user2['id']]  # Usuario 1 crea conversación con Usuario 2
        }
        response = await client.post(
            f"{API_BASE_URL}/conversations/", 
            json=conversation_data, 
            headers=headers1
        )
        
        if response.status_code != 201:
            print(f"❌ Error creando conversación: {response.status_code} - {response.text}")
            return
        
        conversation = response.json()
        conversation_id = conversation['id']
        print(f"✅ Conversación creada: ID {conversation_id}")
        
        # 9. Enviar mensaje de audio desde usuario 1
        print("\n🎵 Enviando mensaje de audio desde usuario 1...")
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio_file': ('message.wav', audio_file, 'audio/wav')}
            data = {'content_type': 'audio'}
            response = await client.post(
                f"{API_BASE_URL}/conversations/{conversation_id}/messages", 
                files=files,
                data=data,
                headers=headers1
            )
        
        if response.status_code != 201:
            print(f"❌ Error enviando mensaje de audio: {response.status_code} - {response.text}")
            return
        
        message = response.json()
        message_id = message['id']
        print(f"✅ Mensaje de audio enviado: ID {message_id}")
        print(f"   📁 Audio URL: {message.get('media_url', 'N/A')}")
        
        # 10. Esperar un poco para que se procese la traducción
        print("\n⏳ Esperando procesamiento de traducción de audio...")
        await asyncio.sleep(3)
        
        # 11. Verificar que se creó la traducción
        print("\n🔍 Verificando creación de traducción automática...")
        response = await client.get(
            f"{API_BASE_URL}/conversations/{conversation_id}/messages",
            headers=headers2
        )
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo mensajes: {response.status_code} - {response.text}")
            return
        
        messages = response.json()
        print(f"✅ Mensajes obtenidos: {len(messages)} mensajes")
        
        # Buscar el mensaje original y su traducción
        original_message = None
        for msg in messages:
            if msg['id'] == message_id:
                original_message = msg
                break
        
        if not original_message:
            print("❌ No se encontró el mensaje original")
            return
        
        print(f"✅ Mensaje original encontrado:")
        print(f"   🆔 ID: {original_message['id']}")
        print(f"   📱 Tipo: {original_message['content_type']}")
        print(f"   📁 Audio: {original_message.get('media_url', 'N/A')}")
        print(f"   👤 Sender: {original_message['sender_id']}")
        
        # Verificar si tiene traducción
        if 'translated_message' in original_message and original_message['translated_message']:
            translated = original_message['translated_message']
            print(f"🎉 ¡TRADUCCIÓN AUTOMÁTICA CREADA!")
            print(f"   🆔 ID traducción: {translated['id']}")
            print(f"   🌐 Idioma destino: {translated['target_language']}")
            print(f"   📱 Tipo contenido: {translated.get('content_type', 'N/A')}")
            print(f"   📁 Audio traducido: {translated.get('media_url', 'N/A')}")
            print(f"   📝 Contenido: {translated.get('translated_content', 'N/A')}")
            
            # Verificar que el archivo de audio traducido existe
            if translated.get('media_url'):
                # Convertir URL a ruta del archivo
                audio_filename = translated['media_url'].split('/')[-1]
                translated_file_path = Path(f"uploads/audio/message_clon/{audio_filename}")
                
                if translated_file_path.exists():
                    file_size = translated_file_path.stat().st_size
                    print(f"✅ Archivo de audio traducido existe: {translated_file_path} ({file_size} bytes)")
                else:
                    print(f"❌ Archivo de audio traducido NO existe: {translated_file_path}")
            
        else:
            print("❌ No se encontró traducción automática")
            print("💡 Verifica los logs del servidor para errores de traducción")
        
        print("\n🏁 Test completado!")

if __name__ == "__main__":
    asyncio.run(test_audio_translation_workflow())
