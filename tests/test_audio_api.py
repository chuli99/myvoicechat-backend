#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de upload de audio
"""
import requests
import os
import tempfile

BASE_URL = "http://localhost:8000/api/v1"

def create_test_audio_file():
    """Crear un archivo de audio temporal para pruebas"""
    # Crear contenido de audio falso en formato WAV básico
    wav_header = bytes([
        # RIFF header
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        # fmt chunk
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Chunk size
        0x01, 0x00,              # Audio format (PCM)
        0x01, 0x00,              # Number of channels
        0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
        0x88, 0x58, 0x01, 0x00,  # Byte rate
        0x02, 0x00,              # Block align
        0x10, 0x00,              # Bits per sample
        # data chunk
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00,  # Data size
    ])
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file.write(wav_header)
    temp_file.close()
    
    return temp_file.name

def test_complete_audio_workflow():
    print("🧪 Iniciando pruebas completas de la API de audio...")
    
    # 1. Crear usuario de prueba
    print("\n1️⃣ Creando usuario de prueba...")
    user_data = {
        "username": "audiotest_user",
        "email": "audiotest@example.com",
        "password": "testpassword123",
        "primary_language": "es"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/register", json=user_data)
        if response.status_code == 200:
            print("✅ Usuario creado exitosamente")
            user_info = response.json()
            print(f"   Usuario ID: {user_info.get('id')}")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Usuario ya existe, continuando...")
        else:
            print(f"❌ Error al crear usuario: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión al crear usuario: {e}")
        return
    
    # 2. Hacer login
    print("\n2️⃣ Haciendo login...")
    login_data = {
        "username": "audiotest_user",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login exitoso")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return
    
    # 3. Crear archivo de audio de prueba
    print("\n3️⃣ Creando archivo de audio de prueba...")
    audio_file_path = create_test_audio_file()
    print(f"✅ Archivo creado: {audio_file_path}")
    
    # 4. Subir audio de referencia
    print("\n4️⃣ Subiendo audio de referencia...")
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {"audio_file": ("test_audio.wav", audio_file, "audio/wav")}
            response = requests.post(
                f"{BASE_URL}/audio/upload-reference-audio",
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            upload_result = response.json()
            print("✅ Audio subido exitosamente")
            print(f"   Mensaje: {upload_result.get('message')}")
            print(f"   URL: {upload_result.get('audio_url')}")
            audio_url = upload_result.get('audio_url')
        else:
            print(f"❌ Error al subir audio: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error al subir audio: {e}")
        return
    
    # 5. Verificar que el usuario tiene el audio
    print("\n5️⃣ Verificando que el usuario tiene el audio...")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            if user_info.get('ref_audio_url'):
                print("✅ Usuario tiene audio de referencia")
                print(f"   URL almacenada: {user_info.get('ref_audio_url')}")
            else:
                print("❌ Usuario no tiene audio de referencia guardado")
        else:
            print(f"❌ Error al obtener info del usuario: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al verificar usuario: {e}")
    
    # 6. Probar descargar el archivo
    print("\n6️⃣ Probando descarga del archivo...")
    if audio_url:
        try:
            # Extraer filename de la URL
            filename = audio_url.split('/')[-1]
            response = requests.get(f"{BASE_URL}/audio/audio/{filename}")
            
            if response.status_code == 200:
                print("✅ Archivo descargado exitosamente")
                print(f"   Content-Type: {response.headers.get('content-type')}")
                print(f"   Tamaño: {len(response.content)} bytes")
            else:
                print(f"❌ Error al descargar archivo: {response.status_code}")
        except Exception as e:
            print(f"❌ Error al descargar archivo: {e}")
    
    # 7. Probar eliminar audio de referencia
    print("\n7️⃣ Probando eliminar audio de referencia...")
    try:
        response = requests.delete(f"{BASE_URL}/audio/delete-reference-audio", headers=headers)
        if response.status_code == 200:
            print("✅ Audio eliminado exitosamente")
            print(f"   Mensaje: {response.json().get('message')}")
        else:
            print(f"❌ Error al eliminar audio: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error al eliminar audio: {e}")
    
    # Limpiar archivo temporal
    try:
        os.unlink(audio_file_path)
        print(f"\n🧹 Archivo temporal eliminado: {audio_file_path}")
    except:
        pass
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_complete_audio_workflow()
