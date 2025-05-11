# MyVoiceChat Backend

Backend API para la aplicación MyVoiceChat.

## Configuración

1. Clona el repositorio:

```bash
git clone <your-repo-url>
cd myvoicechat-backend
```

2. Crea un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:

Copia el archivo `.env.example` a `.env` y actualiza las variables según tu entorno:

```bash
cp .env.example .env
```

5. Configura la base de datos:

Asegúrate de tener PostgreSQL instalado y ejecutando. Crea una base de datos llamada `myvoicedb` o actualiza el archivo `.env` con tu configuración de base de datos.

6. Ejecuta las migraciones:

```bash
alembic revision --autogenerate -m "create tables"
alembic upgrade head
```

## Ejecución

Para iniciar el servidor en modo desarrollo:

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload
```

## Endpoints

La API estará disponible en: `http://localhost:8000`

Documentación de API:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Funcionalidades

- Registro de usuarios
- Autenticación (Login)
- CRUD de usuarios
- Gestión de perfil de usuario
