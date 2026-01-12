#!/usr/bin/env python3
"""
Test script to login and check UI functionality
"""
import requests

BASE_URL = "http://localhost:5000"

def test_login_and_ui():
    """Test login and then check UI functionality"""
    print("🧪 Testing Login and UI Functionality")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Login with demo account
        print("\n1. Testing login with demo account...")
        login_data = {
            'username': 'demo_user',
            'password': 'demo123'
        }
        
        response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            if 'login' in response.url.lower():
                print("❌ Login failed - still on login page")
                return
            else:
                print("✅ Login successful")
        elif response.status_code == 302:
            print(f"✅ Login redirect: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        # Test 2: Check dashboard after login
        print("\n2. Testing dashboard access after login...")
        response = session.get(f"{BASE_URL}/")
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for key elements
            print("\n3. Checking for key UI elements...")
            
            checks = [
                ('Add Card button', 'Add Card' in html_content and 'showAddCard' in html_content),
                ('AI Generate button', 'AI Generate' in html_content and 'showAIGeneration' in html_content),
                ('Manage Folders button', 'Manage Folders' in html_content and 'showFolderManager' in html_content),
                ('Refresh button', 'Refresh' in html_content and 'loadCards' in html_content),
                ('Folders container', 'id="foldersContainer"' in html_content),
                ('Cards list', 'id="cardsList"' in html_content),
                ('Dashboard title', 'Dashboard - Active Recall' in html_content),
            ]
            
            for check_name, check_result in checks:
                print(f"{check_name}: {'✅ Found' if check_result else '❌ Missing'}")
            
            print(f"\n4. Checking JavaScript functions...")
            js_functions = [
                'function showAddCard',
                'function showAIGeneration', 
                'function showFolderManager',
                'function loadFolders',
                'function loadCards',
                'USER_ID ='
            ]
            
            for func in js_functions:
                if func in html_content:
                    print(f"{func}: ✅ Found")
                else:
                    print(f"{func}: ❌ Missing")
            
            # Test 3: Check if folders API works
            print(f"\n5. Testing folders API...")
            response = session.get(f"{BASE_URL}/api/folders")
            print(f"Folders API status: {response.status_code}")
            
            if response.status_code == 200:
                folders_data = response.json()
                print(f"Folders found: {len(folders_data.get('folders', []))}")
                for folder in folders_data.get('folders', [])[:3]:  # Show first 3
                    print(f"  - {folder.get('name', 'Unknown')} ({folder.get('card_count', 0)} cards)")
            else:
                print(f"❌ Folders API failed: {response.status_code}")
                
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_and_ui()