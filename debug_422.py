#!/usr/bin/env python3
import requests
import json
from io import BytesIO

# Configuración
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1"

def test_debug_422():
    print("🔍 Debugeando error 422 en upload-reference-audio...")
    
    # Primero crear un usuario y hacer login
    print("\n1️⃣ Creando usuario de prueba...")
    user_payload = {
        "username": "debug_user",
        "email": "debug@example.com", 
        "password": "password123",
        "primary_language": "es"
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/register", json=user_payload)
        print(f"Register status: {response.status_code}")
        if response.status_code != 200:
            print(f"Register response: {response.text}")
            return
        
        print("\n2️⃣ Haciendo login...")
        login_payload = {
            "username": "debug_user",
            "password": "password123"
        }
        
        response = requests.post(f"{API_BASE}/users/login", json=login_payload)
        print(f"Login status: {response.status_code}")
        if response.status_code != 200:
            print(f"Login response: {response.text}")
            return
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ Login exitoso")
        
        print("\n3️⃣ Probando upload de audio...")
        # Crear archivo de audio de prueba
        audio_content = b"fake audio data for testing"
        
        # Preparar headers con token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Preparar archivo
        files = {
            "audio_file": ("test_debug.wav", BytesIO(audio_content), "audio/wav")
        }
        
        print("Headers:", headers)
        print("Files:", files)
        
        response = requests.post(
            f"{API_BASE}/audio/upload-reference-audio",
            headers=headers,
            files=files
        )
        
        print(f"Upload status: {response.status_code}")
        print(f"Upload response: {response.text}")
        
        if response.status_code == 422:
            print("\n🔍 Error 422 detectado. Analizando...")
            try:
                error_detail = response.json()
                print("Error detail:", json.dumps(error_detail, indent=2))
            except:
                print("No se pudo parsear la respuesta como JSON")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_endpoint_exists():
    """Verificar que el endpoint existe"""
    print("🔍 Verificando endpoints disponibles...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger docs disponibles en /docs")
        
        # Verificar OpenAPI spec
        response = requests.get(f"{API_BASE}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            audio_endpoints = [path for path in paths.keys() if "audio" in path]
            print(f"Endpoints de audio encontrados: {audio_endpoints}")
        
    except Exception as e:
        print(f"Error verificando endpoints: {e}")

if __name__ == "__main__":
    test_endpoint_exists()
    test_debug_422()
