#!/usr/bin/env python3
import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1"

def test_conversations_all_endpoint():
    print("🧪 Probando endpoint /conversations/all...")
    
    try:
        # 1. Crear usuario de prueba y hacer login
        print("\n1️⃣ Creando usuario de prueba...")
        user_payload = {
            "username": "test_conv_user",
            "email": "test_conv@example.com",
            "password": "password123",
            "primary_language": "es"
        }
        
        response = requests.post(f"{API_BASE}/users/register", json=user_payload)
        if response.status_code != 200:
            print(f"❌ Error creando usuario: {response.status_code} - {response.text}")
            return
        
        print("✅ Usuario creado")
        
        # 2. Hacer login
        print("\n2️⃣ Haciendo login...")
        login_payload = {
            "username": "test_conv_user",
            "password": "password123"
        }
        
        response = requests.post(f"{API_BASE}/users/login", json=login_payload)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ Login exitoso")
        
        # 3. Preparar headers con token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 4. Crear algunas conversaciones de prueba
        print("\n3️⃣ Creando conversaciones de prueba...")
        for i in range(3):
            response = requests.post(
                f"{API_BASE}/conversations/",
                headers=headers
            )
            if response.status_code == 200:
                conv_data = response.json()
                print(f"✅ Conversación {i+1} creada: ID {conv_data['id']}")
            else:
                print(f"⚠️ Error creando conversación {i+1}: {response.status_code}")
        
        # 5. Probar endpoint /conversations/all
        print("\n4️⃣ Probando /conversations/all...")
        
        # Sin parámetros
        response = requests.get(
            f"{API_BASE}/conversations/all",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Endpoint funcionando correctamente")
            print(f"📊 Total de conversaciones: {len(conversations)}")
            
            for conv in conversations:
                print(f"  - ID: {conv['id']}, Creado: {conv['created_at']}")
                print(f"    Participantes: {conv['participant_count']}, Mensajes: {conv['message_count']}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")
        
        # 6. Probar con parámetros
        print("\n5️⃣ Probando con parámetros skip y limit...")
        response = requests.get(
            f"{API_BASE}/conversations/all?skip=0&limit=2",
            headers=headers
        )
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Con límite funcionando: {len(conversations)} conversaciones")
        else:
            print(f"❌ Error con parámetros: {response.status_code} - {response.text}")
        
        # 7. Probar sin autenticación (debería fallar)
        print("\n6️⃣ Probando sin autenticación (debería fallar)...")
        response = requests.get(f"{API_BASE}/conversations/all")
        
        if response.status_code == 401:
            print("✅ Endpoint correctamente protegido - requiere autenticación")
        else:
            print(f"⚠️ Endpoint no protegido adecuadamente: {response.status_code}")
        
        print("\n🎉 Pruebas completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en http://localhost:8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

def test_endpoint_documentation():
    """Verificar que el endpoint aparece en la documentación"""
    print("\n📚 Verificando documentación...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            if "/api/v1/conversations/all" in paths:
                endpoint_info = paths["/api/v1/conversations/all"]
                print("✅ Endpoint aparece en documentación:")
                print(f"  Métodos: {list(endpoint_info.keys())}")
                if "get" in endpoint_info:
                    get_info = endpoint_info["get"]
                    print(f"  Descripción: {get_info.get('summary', 'N/A')}")
                    print(f"  Requiere auth: {'security' in get_info}")
            else:
                print("❌ Endpoint no encontrado en documentación")
                available_conv_endpoints = [path for path in paths.keys() if "conversations" in path]
                print(f"Endpoints de conversaciones disponibles: {available_conv_endpoints}")
        else:
            print(f"❌ Error obteniendo documentación: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verificando documentación: {e}")

if __name__ == "__main__":
    test_endpoint_documentation()
    test_conversations_all_endpoint()
