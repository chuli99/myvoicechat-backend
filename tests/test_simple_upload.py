#!/usr/bin/env python3
"""
Simple test just for audio upload
"""
import requests
import json
import io
import wave
import numpy as np

# Server configuration
BASE_URL = "http://localhost:8080/api/v1"

def create_test_audio():
    """Create a simple test audio file in WAV format"""
    # Generate a simple sine wave (440 Hz for 2 seconds)
    sample_rate = 44100
    duration = 2.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(frequency * 2 * np.pi * t)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create a WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

# Login
login_data = {
    "username": "audiotest",
    "password": "testpass123"
}

login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
token_data = login_response.json()
access_token = token_data["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}"
}

# Create conversation
conv_response = requests.post(f"{BASE_URL}/conversations/", headers=headers)
conversation = conv_response.json()
conversation_id = conversation["id"]

print(f"Conversation ID: {conversation_id}")

# Upload audio
audio_data = create_test_audio()
files = {
    'audio_file': ('test_message_audio.wav', audio_data, 'audio/wav')
}

form_data = {
    'conversation_id': str(conversation_id),
    'content': 'Test audio message'
}

upload_response = requests.post(
    f"{BASE_URL}/audio/upload-message-audio",
    files=files,
    data=form_data,
    headers=headers
)

if upload_response.status_code == 200:
    result = upload_response.json()
    print(f"Success: {result}")
    audio_url = result['audio_url']
    
    # Try to download
    download_response = requests.get(f"{BASE_URL}{audio_url}", headers=headers)
    print(f"Download status: {download_response.status_code}")
    
    if download_response.status_code != 200:
        print(f"Download error: {download_response.text}")
else:
    print(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
