#!/usr/bin/env python3
import requests
import json

# URL base de la API
base_url = "http://localhost:8000/api/v1/users"

# Datos del usuario a registrar
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword",
    "primary_language": "es"
}

# Registro de usuario
def register_user():
    print("Registrando usuario...")
    response = requests.post(f"{base_url}/register", json=user_data)
    if response.status_code == 200:
        print("Usuario registrado exitosamente!")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"Error al registrar usuario: {response.status_code}")
        print(response.text)
        return False

# Login de usuario
def login_user():
    print("\nHaciendo login...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = requests.post(f"{base_url}/login/access-token", data=login_data)
    if response.status_code == 200:
        print("Login exitoso!")
        token_data = response.json()
        print(json.dumps(token_data, indent=2))
        return token_data["access_token"]
    else:
        print(f"Error al hacer login: {response.status_code}")
        print(response.text)
        return None

# Obtener información del usuario actual
def get_me(token):
    print("\nObteniendo información del usuario actual...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/users/me", headers=headers)
    if response.status_code == 200:
        print("Información obtenida exitosamente!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error al obtener información: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if register_user():
        token = login_user()
        if token:
            get_me(token)
