#!/usr/bin/env python3
"""
Test the web interface
"""
import requests

def test_web_interface():
    print("🌐 Testing Active Recall Web Interface...")
    
    try:
        # Test the main page
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            if "Active Recall" in response.text:
                print("✅ Page content looks correct")
            else:
                print("❌ Page content seems wrong")
        else:
            print(f"❌ Web interface returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web server")

if __name__ == "__main__":
    test_web_interface()