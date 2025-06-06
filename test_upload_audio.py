import asyncio
import os
from fastapi import UploadFile
from app.services.file_storage import FileStorageService

async def test_file_service():
    # Crear servicio
    service = FileStorageService()
    
    # Crear un archivo de audio de prueba
    test_audio_content = b"fake audio content for testing"
    
    # Simular UploadFile
    class MockUploadFile:
        def __init__(self, filename, content, content_type):
            self.filename = filename
            self.content = content
            self.content_type = content_type
        
        async def read(self):
            return self.content
    
    mock_file = MockUploadFile("test.wav", test_audio_content, "audio/wav")
    
    try:
        # Probar guardar archivo
        file_path = await service.save_audio_file(mock_file, user_id=1)
        filename = os.path.basename(file_path)
        print(f"Archivo guardado: {filename} en {file_path}")
        
        # Verificar que existe
        if os.path.exists(file_path):
            print("✅ Archivo creado correctamente")
        else:
            print("❌ Error: Archivo no encontrado")
        
        # Probar URL
        url = service.get_file_url(file_path)
        print(f"URL generada: {url}")
        
        # Probar eliminación
        if service.delete_audio_file(file_path):
            print("✅ Archivo eliminado correctamente")
        else:
            print("❌ Error al eliminar archivo")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_file_service())