#!/usr/bin/env python3
"""
Simple test script to check UI functionality
"""
import requests

BASE_URL = "http://localhost:5000"

def test_ui_simple():
    """Simple test of the UI functionality"""
    print("🧪 Testing UI Functionality (Simple)")
    print("=" * 50)
    
    try:
        # Test 1: Check if the main page loads
        print("\n1. Testing main page load...")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for key elements
            print("\n2. Checking for key UI elements...")
            
            # Check for buttons
            checks = [
                ('Add Card button', 'Add Card' in html_content and 'showAddCard' in html_content),
                ('AI Generate button', 'AI Generate' in html_content and 'showAIGeneration' in html_content),
                ('Manage Folders button', 'Manage Folders' in html_content and 'showFolderManager' in html_content),
                ('Refresh button', 'Refresh' in html_content and 'loadCards' in html_content),
                ('Folders container', 'id="foldersContainer"' in html_content),
                ('Cards list', 'id="cardsList"' in html_content),
            ]
            
            for check_name, check_result in checks:
                print(f"{check_name}: {'✅ Found' if check_result else '❌ Missing'}")
            
            print(f"\n3. Checking JavaScript functions...")
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
            
            # Check for potential JavaScript issues
            print(f"\n4. Checking for potential issues...")
            
            # Count script tags
            script_count = html_content.count('<script>')
            print(f"Script tags: {script_count}")
            
            # Check for template rendering
            if '{{ user.id }}' in html_content:
                print("Template variables: ❌ Not rendered (user not logged in)")
            elif 'USER_ID = ' in html_content:
                print("Template variables: ✅ Likely rendered")
            
            # Look for common error patterns
            error_patterns = [
                ('Unclosed script tag', '<script>' in html_content and '</script>' not in html_content),
                ('Template syntax in JS', '{% if' in html_content and 'USER_ID' in html_content),
                ('Missing closing braces', html_content.count('{') != html_content.count('}')),
            ]
            
            for pattern_name, has_issue in error_patterns:
                if has_issue:
                    print(f"{pattern_name}: ⚠️ Potential issue detected")
                else:
                    print(f"{pattern_name}: ✅ OK")
                    
        elif response.status_code == 302:
            print(f"Redirect detected. Location: {response.headers.get('Location', 'Unknown')}")
            print("This might indicate authentication is required.")
        else:
            print(f"❌ Failed to load main page: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ui_simple()