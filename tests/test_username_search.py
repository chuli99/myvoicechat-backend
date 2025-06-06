#!/usr/bin/env python3
"""
Test script for the new username search endpoint
"""
import requests
import json

# Server configuration
BASE_URL = "http://localhost:8080/api/v1"

def test_username_search():
    """Test the username search endpoint"""
    
    # First, let's try to create a test user or use an existing one
    print("🔑 Attempting to register a test user...")
    register_data = {
        "username": "searchtest",
        "email": "searchtest@example.com",
        "password": "testpass123",
        "primary_language": "es"
    }
    
    register_response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    
    if register_response.status_code in [200, 201]:
        print("✅ Test user created successfully!")
    elif register_response.status_code == 400:
        print("ℹ️ Test user already exists, continuing with existing user...")
    else:
        print(f"⚠️ Registration response: {register_response.status_code} - {register_response.text}")
    
    # Now try to login with the test user
    login_data = {
        "username": "searchtest",
        "password": "testpass123"
    }
    
    print("🔑 Attempting login...")
    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful! User ID: {token_data.get('user_id')}")
        
        # Prepare headers with authorization
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Search for the logged-in user
        print(f"\n🔍 Testing username search for: {login_data['username']}")
        search_response = requests.get(
            f"{BASE_URL}/users/search/{login_data['username']}", 
            headers=headers
        )
        
        if search_response.status_code == 200:
            user_data = search_response.json()
            print(f"✅ User found: {json.dumps(user_data, indent=2)}")
        else:
            print(f"❌ Search failed: {search_response.status_code} - {search_response.text}")
        
        # Test 2: Search for a non-existent user
        print(f"\n🔍 Testing search for non-existent user: 'nonexistentuser'")
        search_response = requests.get(
            f"{BASE_URL}/users/search/nonexistentuser", 
            headers=headers
        )
        
        if search_response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent user")
            print(f"Response: {search_response.json()}")
        else:
            print(f"❌ Unexpected response: {search_response.status_code} - {search_response.text}")
        
        # Test 3: Get all users to see what usernames are available
        print(f"\n📋 Getting all users to see available usernames...")
        users_response = requests.get(f"{BASE_URL}/users/users", headers=headers)
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ Found {len(users)} users:")
            for user in users[:5]:  # Show first 5 users
                print(f"  - ID: {user['id']}, Username: {user['username']}")
            
            # Test search with another existing user if available
            if len(users) > 1:
                test_username = users[1]['username']  # Pick second user
                print(f"\n🔍 Testing search for another user: '{test_username}'")
                search_response = requests.get(
                    f"{BASE_URL}/users/search/{test_username}", 
                    headers=headers
                )
                
                if search_response.status_code == 200:
                    user_data = search_response.json()
                    print(f"✅ User found: {json.dumps(user_data, indent=2)}")
                else:
                    print(f"❌ Search failed: {search_response.status_code} - {search_response.text}")
        else:
            print(f"❌ Failed to get users: {users_response.status_code} - {users_response.text}")
            
    else:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        print("Make sure you have a user with username 'testuser' and password 'testpassword123'")
        print("Or modify the login_data in this script to use an existing user")

if __name__ == "__main__":
    print("🧪 Testing username search endpoint")
    print("=" * 50)
    test_username_search()
