from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.endpoints import api_router
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
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for audio uploads - this serves files at /api/uploads/...
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="api_uploads")

# Mount static files for template resources
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "template")), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join(os.path.dirname(__file__), "template", "login.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/test-audio", response_class=HTMLResponse)
def test_audio():
    html_path = os.path.join(os.path.dirname(__file__), "template", "test_audio_upload.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/conversation-ws", response_class=HTMLResponse)
def conversation_ws():
    html_path = os.path.join(os.path.dirname(__file__), "template", "conversation_ws.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
