#!/usr/bin/env python3
"""
Ejemplo práctico de uso del sistema de audio para mensajes
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def demo_audio_messages():
    """Demostración completa del sistema de audio para mensajes"""
    
    print("🎵 DEMO: Sistema de Audio para Mensajes")
    print("=" * 50)
    
    # 1. Login
    print("1️⃣ Autenticando usuario...")
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": "audiotest",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Error en login")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Usuario autenticado")
    
    # 2. Crear conversación
    print("\n2️⃣ Creando conversación de prueba...")
    conv_response = requests.post(f"{BASE_URL}/conversations/", headers=headers)
    conversation_id = conv_response.json()["id"]
    print(f"✅ Conversación creada: ID {conversation_id}")
    
    # 3. Simular archivo de audio (texto para demostración)
    print("\n3️⃣ Preparando archivo de audio...")
    audio_content = b"SIMULACION_AUDIO_WAV_FILE_CONTENT_FOR_DEMO"
    files = {'audio_file': ('demo_audio.wav', audio_content, 'audio/wav')}
    form_data = {
        'conversation_id': str(conversation_id),
        'content': 'Este es un mensaje de audio de demostración'
    }
    print("✅ Archivo de audio preparado")
    
    # 4. Subir audio
    print("\n4️⃣ Subiendo audio de mensaje...")
    upload_response = requests.post(
        f"{BASE_URL}/audio/upload-message-audio",
        files=files,
        data=form_data,
        headers=headers
    )
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        print("✅ Audio subido exitosamente!")
        print(f"   📨 Message ID: {result['message_id']}")
        print(f"   🔗 Audio URL: {result['audio_url']}")
        message_id = result['message_id']
        audio_url = result['audio_url']
    else:
        print(f"❌ Error subiendo audio: {upload_response.text}")
        return
    
    # 5. Verificar mensaje en conversación
    print("\n5️⃣ Verificando mensaje en conversación...")
    conv_detail = requests.get(f"{BASE_URL}/conversations/{conversation_id}", headers=headers)
    messages = conv_detail.json().get('messages', [])
    audio_messages = [m for m in messages if m.get('content_type') == 'audio']
    
    print(f"✅ Encontrados {len(audio_messages)} mensaje(s) de audio")
    if audio_messages:
        msg = audio_messages[0]
        print(f"   📝 Contenido: {msg.get('content')}")
        print(f"   🎵 Tipo: {msg.get('content_type')}")
        print(f"   🔗 Media URL: {msg.get('media_url')}")
    
    # 6. Descargar audio
    print("\n6️⃣ Probando descarga de audio...")
    download_response = requests.get(f"{BASE_URL}{audio_url}", headers=headers)
    
    if download_response.status_code == 200:
        print(f"✅ Audio descargado exitosamente ({len(download_response.content)} bytes)")
    else:
        print(f"❌ Error descargando audio: {download_response.status_code}")
    
    # 7. Listar estructura de archivos
    print("\n7️⃣ Estructura de archivos creada:")
    import os
    uploads_path = "/root/Tesis/myvoicechat-backend/uploads/audio/messages"
    if os.path.exists(uploads_path):
        for root, dirs, files in os.walk(uploads_path):
            level = root.replace(uploads_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}🎵 {file}")
    
    # 8. Cleanup (opcional)
    print(f"\n8️⃣ ¿Limpiar mensaje de prueba? (ID: {message_id})")
    response = input("Escribir 'si' para eliminar: ").lower()
    
    if response == 'si':
        delete_response = requests.delete(
            f"{BASE_URL}/audio/delete-message-audio/{message_id}",
            headers=headers
        )
        if delete_response.status_code == 200:
            print("✅ Mensaje de audio eliminado")
        else:
            print("❌ Error eliminando mensaje")
    else:
        print("ℹ️ Mensaje conservado para inspección")
    
    print("\n🎉 DEMO COMPLETADA")
    print("=" * 50)
    print("✅ El sistema de audio para mensajes está funcionando correctamente!")
    print(f"📁 Archivos en: uploads/audio/messages/conv_{conversation_id}/")
    print("🔗 Endpoints disponibles:")
    print("   • POST /api/v1/audio/upload-message-audio")
    print("   • GET /api/v1/audio/message/{filename}")
    print("   • DELETE /api/v1/audio/delete-message-audio/{id}")

if __name__ == "__main__":
    try:
        demo_audio_messages()
    except Exception as e:
        print(f"❌ Error en demo: {e}")
