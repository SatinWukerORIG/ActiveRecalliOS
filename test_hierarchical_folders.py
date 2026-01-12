#!/usr/bin/env python3
"""
Test script for hierarchical folder functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_hierarchical_folders():
    """Test the hierarchical folder system"""
    print("🧪 Testing Hierarchical Folder System")
    print("=" * 50)
    
    # Test 1: Get root folders (should be empty initially)
    print("\n1. Testing root folder retrieval...")
    response = requests.get(f"{BASE_URL}/api/folders")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Root folders: {len(data['folders'])}")
        print(f"Parent ID: {data.get('parent_id')}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Create a root folder
    print("\n2. Creating root folder 'Mathematics'...")
    folder_data = {
        "name": "Mathematics",
        "description": "Math subjects and topics",
        "color": "#007AFF"
    }
    response = requests.post(f"{BASE_URL}/api/folders", 
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(folder_data))
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        math_folder = response.json()['folder']
        math_folder_id = math_folder['id']
        print(f"Created folder ID: {math_folder_id}")
        print(f"Folder path: {math_folder.get('path', [])}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 3: Create a subfolder
    print(f"\n3. Creating subfolder 'Calculus' under Mathematics...")
    subfolder_data = {
        "name": "Calculus",
        "description": "Calculus concepts and formulas",
        "color": "#28a745",
        "parent_folder_id": math_folder_id
    }
    response = requests.post(f"{BASE_URL}/api/folders",
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(subfolder_data))
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        calculus_folder = response.json()['folder']
        calculus_folder_id = calculus_folder['id']
        print(f"Created subfolder ID: {calculus_folder_id}")
        print(f"Parent folder ID: {calculus_folder.get('parent_folder_id')}")
        print(f"Folder path: {calculus_folder.get('path', [])}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 4: Get subfolders of Mathematics
    print(f"\n4. Getting subfolders of Mathematics (ID: {math_folder_id})...")
    response = requests.get(f"{BASE_URL}/api/folders?parent_id={math_folder_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Subfolders found: {len(data['folders'])}")
        for folder in data['folders']:
            print(f"  - {folder['name']} (ID: {folder['id']}, Parent: {folder.get('parent_folder_id')})")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Get folder details with cards and subfolders
    print(f"\n5. Getting Mathematics folder details...")
    response = requests.get(f"{BASE_URL}/api/folders/{math_folder_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        folder_data = response.json()['folder']
        print(f"Folder: {folder_data['name']}")
        print(f"Cards in folder: {len(folder_data.get('cards', []))}")
        print(f"Subfolders: {len(folder_data.get('subfolders', []))}")
        print(f"Total card count: {folder_data.get('total_card_count', 0)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 6: Get all folders (flat list for notifications)
    print(f"\n6. Getting all folders (flat list)...")
    response = requests.get(f"{BASE_URL}/api/folders/all")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total folders: {len(data['folders'])}")
        for folder in data['folders']:
            path_str = " > ".join(folder.get('path', [folder['name']]))
            print(f"  - {path_str} (ID: {folder['id']})")
    else:
        print(f"Error: {response.text}")
    
    print("\n✅ Hierarchical folder tests completed!")
    print(f"Created folders: Mathematics (ID: {math_folder_id}), Calculus (ID: {calculus_folder_id})")

if __name__ == "__main__":
    try:
        test_hierarchical_folders()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")