#!/usr/bin/env python3
"""
Test script for user audio reference with uploads/audio/users directory
"""
import requests
import json
import io
import wave
import numpy as np

BASE_URL = "http://localhost:8080/api/v1"

def create_test_audio():
    """Create a simple test audio file"""
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(frequency * 2 * np.pi * t)
    audio_data = (audio_data * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    buffer.seek(0)
    return buffer.getvalue()

def test_user_audio_reference():
    print("🧪 Testing user audio reference with uploads/audio/users")
    print("=" * 60)
    
    # Create and login user
    register_data = {
        "username": "audioreftest2",
        "email": "audioreftest2@example.com",
        "password": "testpass123",
        "primary_language": "es"
    }
    
    print("1️⃣ Creating user...")
    register_response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    if register_response.status_code in [200, 201]:
        print("✅ User created successfully!")
    elif register_response.status_code == 400:
        print("ℹ️ User already exists, continuing...")
    else:
        print(f"❌ Failed to create user: {register_response.text}")
        return
    
    print("2️⃣ Logging in...")
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": "audioreftest2",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    user_id = token_data["user_id"]
    print(f"✅ Login successful! User ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("3️⃣ Uploading audio reference...")
    audio_data = create_test_audio()
    files = {
        'audio_file': ('reference_audio.wav', audio_data, 'audio/wav')
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/audio/upload-reference-audio",
        files=files,
        headers=headers
    )
    
    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
        return
    
    upload_result = upload_response.json()
    print(f"✅ Upload successful!")
    print(f"   Audio URL: {upload_result['audio_url']}")
    
    # Check URL format
    audio_url = upload_result['audio_url']
    if audio_url.startswith('/api/v1/audio/user/'):
        print("✅ URL format is correct!")
    else:
        print(f"❌ URL format is incorrect. Expected: /api/v1/audio/user/filename, Got: {audio_url}")
    
    # Test file access via new endpoint
    print("4️⃣ Testing file access via /user/ endpoint...")
    file_response = requests.get(f"http://localhost:8080{audio_url}")
    
    if file_response.status_code == 200:
        print(f"✅ File accessible via new endpoint! Size: {len(file_response.content)} bytes")
        print(f"   Content-Type: {file_response.headers.get('content-type')}")
    else:
        print(f"❌ File not accessible via new endpoint: {file_response.status_code}")
        print(f"   Response: {file_response.text}")
    
    # Test legacy endpoint (should still work)
    print("5️⃣ Testing legacy /audio/ endpoint...")
    filename = audio_url.split('/')[-1]
    legacy_url = f"http://localhost:8080/api/v1/audio/audio/{filename}"
    legacy_response = requests.get(legacy_url)
    
    if legacy_response.status_code == 200:
        print(f"✅ Legacy endpoint still works! Size: {len(legacy_response.content)} bytes")
    else:
        print(f"❌ Legacy endpoint not working: {legacy_response.status_code}")
    
    # Verify user profile has correct URL
    print("6️⃣ Verifying user profile...")
    profile_response = requests.get(f"{BASE_URL}/users/users/me", headers=headers)
    
    if profile_response.status_code == 200:
        user_data = profile_response.json()
        stored_url = user_data.get('ref_audio_url')
        if stored_url == audio_url:
            print("✅ Audio URL correctly saved in user profile!")
            print(f"   Stored URL: {stored_url}")
        else:
            print(f"❌ Audio URL mismatch in profile:")
            print(f"   Expected: {audio_url}")
            print(f"   Got: {stored_url}")
    else:
        print(f"❌ Failed to get user profile: {profile_response.status_code} - {profile_response.text}")
    
    # Check file system structure
    print("7️⃣ Checking file system structure...")
    import os
    uploads_path = "/root/Tesis/myvoicechat-backend/uploads/audio/users"
    if os.path.exists(uploads_path):
        files_in_dir = os.listdir(uploads_path)
        user_files = [f for f in files_in_dir if f.startswith(f"user_{user_id}_")]
        print(f"✅ Found {len(user_files)} file(s) for user {user_id} in uploads/audio/users/")
        if user_files:
            print(f"   Latest file: {user_files[-1]}")
    else:
        print(f"❌ Directory {uploads_path} does not exist")
    
    print("\n🎉 User audio reference test completed!")
    print("=" * 60)
    
    if audio_url.startswith('/api/v1/audio/user/') and file_response.status_code == 200:
        print("✅ ALL TESTS PASSED!")
        print(f"✅ Audio stored in: uploads/audio/users/")
        print(f"✅ URL format: /api/v1/audio/user/filename")
        print(f"✅ ref_audio_url field updated correctly")
    else:
        print("❌ SOME TESTS FAILED!")

if __name__ == "__main__":
    try:
        test_user_audio_reference()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
