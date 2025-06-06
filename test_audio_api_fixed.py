import requests
import json
import os
from io import BytesIO

# Configuración de la API
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1"

# Headers por defecto
headers = {
    "Content-Type": "application/json"
}

async def test_complete_audio_api():
    print("🧪 Iniciando pruebas completas de la API de audio...")
    
    # Variables para almacenar datos entre pruebas
    access_token = None
    user_data = None
    audio_url = None
    
    try:
        print("\n1️⃣ Creando usuario de prueba...")
        # Crear usuario de prueba
        user_payload = {
            "username": "testuser_audio",
            "email": "testuser_audio@example.com",
            "password": "testpassword123",
            "primary_language": "es"
        }
        
        response = requests.post(f"{API_BASE}/users/register", json=user_payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Usuario creado exitosamente: {user_data['username']}")
        else:
            print(f"❌ Error al crear usuario: {response.status_code} - {response.text}")
            return
        
        print("\n2️⃣ Haciendo login...")
        # Hacer login
        login_payload = {
            "username": "testuser_audio",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{API_BASE}/users/login", json=login_payload, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            login_data = response.json()
            access_token = login_data["access_token"]
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return
        
        print("\n3️⃣ Probando subir archivo de audio...")
        # Subir archivo de audio
        auth_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Crear un archivo de audio falso
        audio_content = b"fake audio content for testing API"
        audio_file = BytesIO(audio_content)
        
        files = {
            "audio_file": ("test_api.wav", audio_file, "audio/wav")
        }
        
        response = requests.post(
            f"{API_BASE}/audio/upload-reference-audio", 
            files=files, 
            headers=auth_headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            upload_data = response.json()
            audio_url = upload_data["audio_url"]
            print(f"✅ Audio subido exitosamente")
            print(f"🔗 URL del audio: {audio_url}")
        else:
            print(f"❌ Error al subir audio: {response.status_code} - {response.text}")
            return
        
        print("\n4️⃣ Verificando que el usuario tiene el audio...")
        # Obtener información del usuario actual
        response = requests.get(f"{API_BASE}/users/users/me", headers=auth_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            current_user = response.json()
            if current_user.get("ref_audio_url"):
                print(f"✅ Usuario tiene audio de referencia: {current_user['ref_audio_url']}")
            else:
                print("❌ Usuario no tiene audio de referencia en la BD")
        else:
            print(f"❌ Error al obtener usuario: {response.status_code} - {response.text}")
        
        print("\n5️⃣ Probando descargar archivo de audio...")
        # Intentar descargar el archivo
        if audio_url:
            filename = audio_url.split("/")[-1]
            response = requests.get(f"{API_BASE}/audio/audio/{filename}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Archivo descargado exitosamente")
                print(f"📦 Tamaño del archivo: {len(response.content)} bytes")
                print(f"🎵 Content-Type: {response.headers.get('content-type', 'No especificado')}")
            else:
                print(f"❌ Error al descargar archivo: {response.status_code}")
        
        print("\n6️⃣ Probando subir archivo que no es audio...")
        # Probar con archivo que no es audio
        text_content = b"this is not an audio file"
        text_file = BytesIO(text_content)
        
        files = {
            "audio_file": ("test.txt", text_file, "text/plain")
        }
        
        response = requests.post(
            f"{API_BASE}/audio/upload-reference-audio", 
            files=files, 
            headers=auth_headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctamente rechazó archivo que no es audio")
        else:
            print(f"❌ Debería haber rechazado el archivo: {response.status_code} - {response.text}")
        
        print("\n7️⃣ Probando eliminar audio de referencia...")
        # Eliminar audio de referencia
        response = requests.delete(f"{API_BASE}/audio/delete-reference-audio", headers=auth_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Audio de referencia eliminado exitosamente")
        else:
            print(f"❌ Error al eliminar audio: {response.status_code} - {response.text}")
        
        print("\n8️⃣ Verificando que el audio fue eliminado...")
        # Verificar que ya no tiene audio
        response = requests.get(f"{API_BASE}/users/users/me", headers=auth_headers)
        if response.status_code == 200:
            current_user = response.json()
            if not current_user.get("ref_audio_url"):
                print("✅ Audio de referencia eliminado de la BD")
            else:
                print(f"❌ Audio aún presente en BD: {current_user['ref_audio_url']}")
        
        print("\n🎉 ¡Todas las pruebas completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

def test_server_status():
    """Verificar que el servidor esté ejecutándose"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Servidor está ejecutándose")
            return True
        else:
            print(f"❌ Servidor responde pero con error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor en http://localhost:8000")
        print("💡 Ejecuta: uvicorn app.main:app --reload")
        return False

if __name__ == "__main__":
    print("🔍 Verificando estado del servidor...")
    if test_server_status():
        import asyncio
        asyncio.run(test_complete_audio_api())
