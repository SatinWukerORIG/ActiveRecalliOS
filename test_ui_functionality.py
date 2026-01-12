#!/usr/bin/env python3
"""
Test script to check UI functionality by examining the rendered HTML
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

def test_ui_functionality():
    """Test the UI functionality by checking the rendered HTML"""
    print("🧪 Testing UI Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Check if the main page loads
        print("\n1. Testing main page load...")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for key elements
            print("\n2. Checking for key UI elements...")
            
            # Check for buttons
            add_card_btn = soup.find('button', string=lambda text: text and 'Add Card' in text)
            ai_generate_btn = soup.find('button', string=lambda text: text and 'AI Generate' in text)
            manage_folders_btn = soup.find('button', string=lambda text: text and 'Manage Folders' in text)
            refresh_btn = soup.find('button', string=lambda text: text and 'Refresh' in text)
            
            print(f"Add Card button: {'✅ Found' if add_card_btn else '❌ Missing'}")
            print(f"AI Generate button: {'✅ Found' if ai_generate_btn else '❌ Missing'}")
            print(f"Manage Folders button: {'✅ Found' if manage_folders_btn else '❌ Missing'}")
            print(f"Refresh button: {'✅ Found' if refresh_btn else '❌ Missing'}")
            
            # Check for onclick handlers
            print(f"Add Card onclick: {add_card_btn.get('onclick') if add_card_btn else 'N/A'}")
            print(f"AI Generate onclick: {ai_generate_btn.get('onclick') if ai_generate_btn else 'N/A'}")
            
            # Check for folders container
            folders_container = soup.find('div', id='foldersContainer')
            print(f"Folders container: {'✅ Found' if folders_container else '❌ Missing'}")
            
            # Check for JavaScript
            scripts = soup.find_all('script')
            js_content = ""
            for script in scripts:
                if script.string:
                    js_content += script.string
            
            print(f"\n3. Checking JavaScript functions...")
            js_functions = [
                'showAddCard',
                'showAIGeneration', 
                'showFolderManager',
                'loadFolders',
                'loadCards'
            ]
            
            for func in js_functions:
                if f'function {func}' in js_content or f'{func} =' in js_content:
                    print(f"{func}: ✅ Found")
                else:
                    print(f"{func}: ❌ Missing")
            
            # Check for syntax errors in JavaScript
            print(f"\n4. Checking for common JavaScript issues...")
            
            # Look for unclosed braces or syntax issues
            open_braces = js_content.count('{')
            close_braces = js_content.count('}')
            print(f"Brace balance: {open_braces} open, {close_braces} close ({'✅ Balanced' if open_braces == close_braces else '❌ Unbalanced'})")
            
            # Look for template syntax issues
            if '{% if' in js_content and '{% endif %}' in js_content:
                print("Template syntax: ✅ Flask templates found (normal)")
            
            # Check for USER_ID initialization
            if 'USER_ID =' in js_content:
                print("USER_ID initialization: ✅ Found")
            else:
                print("USER_ID initialization: ❌ Missing")
                
        else:
            print(f"❌ Failed to load main page: {response.status_code}")
            if response.status_code == 302:
                print(f"Redirect location: {response.headers.get('Location', 'Unknown')}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ui_functionality()