from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import users
from app.core.config import settings
from app.db.database import create_tables


# Crear las tablas si no existen
try:
    create_tables()
    print("Tablas creadas exitosamente")
except Exception as e:
    print(f"Error al crear tablas: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, deberías especificar tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])


@app.get("/")
def root():
    return {"message": "Welcome to MyVoiceChat API"}
