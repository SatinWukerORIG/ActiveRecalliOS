#!/usr/bin/env python3
"""
Test script for folder and delete functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_folder_functionality():
    """Test folder creation, card organization, and deletion"""
    print("🧪 Testing Folder and Delete Functionality")
    print("=" * 50)
    
    # Test data
    test_user = {
        "username": "test_folder_user",
        "email": "testfolder@example.com",
        "password": "testpass123"
    }
    
    session = requests.Session()
    
    try:
        # 1. Register and login
        print("1. Setting up test user...")
        register_response = session.post(f"{BASE_URL}/api/auth/register", json=test_user)
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        print("✅ User setup complete")
        
        # 2. Create a folder
        print("\n2. Creating a test folder...")
        folder_data = {
            "name": "Test Biology",
            "description": "Biology study materials",
            "color": "#28a745"
        }
        
        folder_response = session.post(f"{BASE_URL}/api/folders", json=folder_data)
        print(f"Create folder response: {folder_response.status_code}")
        
        if folder_response.status_code == 201:
            folder_result = folder_response.json()
            folder_id = folder_result['folder']['id']
            print(f"✅ Folder created successfully with ID: {folder_id}")
        else:
            print(f"❌ Folder creation failed: {folder_response.text}")
            return
        
        # 3. Get folders list
        print("\n3. Getting folders list...")
        folders_response = session.get(f"{BASE_URL}/api/folders")
        if folders_response.status_code == 200:
            folders = folders_response.json()
            print(f"✅ Found {len(folders['folders'])} folder(s)")
            for folder in folders['folders']:
                print(f"   - {folder['name']} ({folder['card_count']} cards)")
        else:
            print(f"❌ Failed to get folders: {folders_response.status_code}")
        
        # 4. Create a card in the folder
        print("\n4. Creating a card in the folder...")
        card_data = {
            "user_id": login_response.json()['user']['id'],
            "folder_id": folder_id,
            "content_type": "flashcard",
            "front": "What is photosynthesis?",
            "back": "The process by which plants convert sunlight into energy",
            "subject": "Biology"
        }
        
        card_response = session.post(f"{BASE_URL}/api/cards", json=card_data)
        print(f"Create card response: {card_response.status_code}")
        
        if card_response.status_code == 201:
            card_result = card_response.json()
            card_id = card_result['card']['id']
            print(f"✅ Card created successfully with ID: {card_id}")
        else:
            print(f"❌ Card creation failed: {card_response.text}")
            return
        
        # 5. Get folder with cards
        print("\n5. Getting folder with cards...")
        folder_detail_response = session.get(f"{BASE_URL}/api/folders/{folder_id}")
        if folder_detail_response.status_code == 200:
            folder_detail = folder_detail_response.json()
            print(f"✅ Folder '{folder_detail['folder']['name']}' has {len(folder_detail['folder']['cards'])} card(s)")
        else:
            print(f"❌ Failed to get folder details: {folder_detail_response.status_code}")
        
        # 6. Test card deletion
        print("\n6. Testing card deletion...")
        delete_card_response = session.delete(f"{BASE_URL}/api/cards/{card_id}")
        print(f"Delete card response: {delete_card_response.status_code}")
        
        if delete_card_response.status_code == 200:
            print("✅ Card deleted successfully")
        else:
            print(f"❌ Card deletion failed: {delete_card_response.text}")
        
        # 7. Test folder deletion
        print("\n7. Testing folder deletion...")
        delete_folder_response = session.delete(f"{BASE_URL}/api/folders/{folder_id}", 
                                               headers={'Content-Type': 'application/json'},
                                               json={"delete_cards": False})
        print(f"Delete folder response: {delete_folder_response.status_code}")
        
        if delete_folder_response.status_code == 200:
            print("✅ Folder deleted successfully")
        else:
            print(f"❌ Folder deletion failed: {delete_folder_response.text}")
        
        print("\n🎉 Folder and delete functionality test completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_folder_functionality()