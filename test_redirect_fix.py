#!/usr/bin/env python3
"""
Test script to verify the redirect loop fix
"""
import requests
import time

def test_redirect_fix():
    """Test that the redirect loop is fixed"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing redirect loop fix...")
    
    # Test 1: Access root URL without authentication
    print("\n1. Testing root URL without authentication...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        if "/welcome" in response.url:
            print("   ✅ Correctly redirected to welcome page")
        else:
            print("   ❌ Unexpected redirect")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Access login page
    print("\n2. Testing login page...")
    try:
        response = requests.get(f"{base_url}/login", allow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        if "/login" in response.url and response.status_code == 200:
            print("   ✅ Login page loads correctly")
        else:
            print("   ❌ Login page issue")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Access welcome page
    print("\n3. Testing welcome page...")
    try:
        response = requests.get(f"{base_url}/welcome", allow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        if "/welcome" in response.url and response.status_code == 200:
            print("   ✅ Welcome page loads correctly")
        else:
            print("   ❌ Welcome page issue")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test auth validation endpoint
    print("\n4. Testing auth validation...")
    try:
        response = requests.get(f"{base_url}/api/auth/validate")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Auth validation correctly returns 401 for unauthenticated user")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Test login with demo credentials and dashboard access
    print("\n5. Testing login and dashboard access...")
    try:
        login_data = {
            "username": "demo_user",
            "password": "demo123"
        }
        
        # Create a session to maintain cookies
        session = requests.Session()
        
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Demo login successful")
            print(f"   User: {result.get('user', {}).get('username', 'Unknown')}")
            
            # Test authenticated dashboard access
            dashboard_response = session.get(f"{base_url}/", allow_redirects=True)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            print(f"   Dashboard URL: {dashboard_response.url}")
            
            if dashboard_response.status_code == 200 and "Active Recall" in dashboard_response.text:
                print("   ✅ Dashboard loads correctly after login")
            else:
                print("   ❌ Dashboard access failed")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 Redirect loop fix test completed!")
    print("\nTo test manually:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. You should see the welcome page (no infinite redirects)")
    print("3. Click 'Login to Your Account' to access the login page")
    print("4. Use demo_user / demo123 to test login functionality")

if __name__ == "__main__":
    test_redirect_fix()