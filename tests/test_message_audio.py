#!/usr/bin/env python3
"""
Test script for message audio upload functionality
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

def test_message_audio_upload():
    """Test the message audio upload functionality"""
    
    # First, register and login a test user
    print("🔑 Setting up test user...")
    register_data = {
        "username": "audiotest",
        "email": "audiotest@example.com",
        "password": "testpass123",
        "primary_language": "es"
    }
    
    register_response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    if register_response.status_code in [200, 201]:
        print("✅ Test user created successfully!")
    elif register_response.status_code == 400:
        print("ℹ️ Test user already exists, continuing...")
    
    # Login
    login_data = {
        "username": "audiotest",
        "password": "testpass123"
    }
    
    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    user_id = token_data["user_id"]
    print(f"✅ Login successful! User ID: {user_id}")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create a test conversation
    print("\n💬 Creating test conversation...")
    conv_response = requests.post(f"{BASE_URL}/conversations/", headers=headers)
    if conv_response.status_code not in [200, 201]:
        print(f"❌ Failed to create conversation: {conv_response.status_code} - {conv_response.text}")
        return
    
    conversation = conv_response.json()
    conversation_id = conversation["id"]
    print(f"✅ Conversation created! ID: {conversation_id}")
    
    # Test 1: Upload message audio
    print("\n🎵 Testing message audio upload...")
    audio_data = create_test_audio()
    
    files = {
        'audio_file': ('test_message_audio.wav', audio_data, 'audio/wav')
    }
    
    form_data = {
        'conversation_id': str(conversation_id),
        'content': 'This is a test audio message'
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/audio/upload-message-audio",
        files=files,
        data=form_data,
        headers=headers
    )
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        print(f"✅ Audio uploaded successfully!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Audio URL: {result['audio_url']}")
        print(f"   Conversation ID: {result['conversation_id']}")
        
        audio_url = result['audio_url']
        message_id = result['message_id']
        
        # Test 2: Download the audio file
        print(f"\n⬇️ Testing audio download...")
        download_response = requests.get(f"{BASE_URL}{audio_url}", headers=headers)
        
        if download_response.status_code == 200:
            print(f"✅ Audio download successful! File size: {len(download_response.content)} bytes")
        else:
            print(f"❌ Audio download failed: {download_response.status_code}")
        
        # Test 3: Check message in conversation
        print(f"\n📖 Checking conversation messages...")
        conv_detail_response = requests.get(f"{BASE_URL}/conversations/{conversation_id}", headers=headers)
        
        if conv_detail_response.status_code == 200:
            conv_detail = conv_detail_response.json()
            messages = conv_detail.get('messages', [])
            audio_messages = [msg for msg in messages if msg.get('content_type') == 'audio']
            print(f"✅ Found {len(audio_messages)} audio message(s) in conversation")
            
            if audio_messages:
                msg = audio_messages[0]
                print(f"   Content: {msg.get('content')}")
                print(f"   Media URL: {msg.get('media_url')}")
                print(f"   Content Type: {msg.get('content_type')}")
        else:
            print(f"❌ Failed to get conversation: {conv_detail_response.status_code}")
        
        # Test 4: Delete the audio message
        print(f"\n🗑️ Testing audio message deletion...")
        delete_response = requests.delete(
            f"{BASE_URL}/audio/delete-message-audio/{message_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("✅ Audio message deleted successfully!")
        else:
            print(f"❌ Delete failed: {delete_response.status_code} - {delete_response.text}")
        
    else:
        print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
    
    # Test 5: Test upload without conversation (should fail)
    print(f"\n🚫 Testing upload without valid conversation...")
    files = {
        'audio_file': ('test_invalid.wav', audio_data, 'audio/wav')
    }
    
    form_data = {
        'conversation_id': '99999',  # Non-existent conversation
        'content': 'This should fail'
    }
    
    invalid_upload_response = requests.post(
        f"{BASE_URL}/audio/upload-message-audio",
        files=files,
        data=form_data,
        headers=headers
    )
    
    if invalid_upload_response.status_code != 200:
        print(f"✅ Correctly rejected invalid conversation: {invalid_upload_response.status_code}")
    else:
        print(f"❌ Should have rejected invalid conversation")

if __name__ == "__main__":
    print("🧪 Testing message audio upload functionality")
    print("=" * 60)
    try:
        test_message_audio_upload()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    print("\n🏁 Test completed!")
