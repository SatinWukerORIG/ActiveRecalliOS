#!/usr/bin/env python3
"""
Test script for new AI generation features with gpt-5-nano, PDF, and image support
"""
import requests
import json
import os

BASE_URL = "http://localhost:5000"

def test_user_registration_and_login():
    """Test user registration and login"""
    print("🔐 Testing user registration and login...")
    
    # Register a test user
    register_data = {
        "username": "testuser_ai",
        "email": "testuser_ai@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ User registered successfully")
    elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
        print("ℹ️ User already exists, proceeding with login")
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None
    
    # Login
    login_data = {
        "username": "testuser_ai",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        session_token = response.json()['session_token']
        print("✅ Login successful")
        return session_token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_text_based_generation(session_token):
    """Test AI generation with text input"""
    print("\n📝 Testing text-based AI generation...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    
    # Test data
    form_data = {
        'source_material': """
        Photosynthesis is the process by which plants convert light energy into chemical energy.
        The process occurs in chloroplasts and involves two main stages:
        1. Light-dependent reactions (occur in thylakoids)
        2. Light-independent reactions (Calvin cycle, occurs in stroma)
        
        The overall equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
        """,
        'generation_type': 'mixed',
        'subject': 'Biology',
        'focus_areas': 'equations, processes, locations',
        'max_cards': '8'
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-content", headers=headers, data=form_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} cards successfully")
        print("📋 Sample generated content:")
        for i, card in enumerate(result['cards'][:3], 1):
            print(f"  {i}. [{card['content_type'].upper()}] {card['front']}")
            if card.get('back'):
                print(f"     Answer: {card['back']}")
        return True
    else:
        print(f"❌ Generation failed: {response.json()}")
        return False

def test_pdf_generation(session_token):
    """Test AI generation with PDF upload (simulated)"""
    print("\n📄 Testing PDF-based AI generation...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    
    # Create a simple test PDF content (simulated)
    # In a real test, you would upload an actual PDF file
    form_data = {
        'source_material': 'Additional context from PDF',
        'generation_type': 'flashcards',
        'subject': 'Chemistry',
        'focus_areas': 'formulas, reactions',
        'max_cards': '5'
    }
    
    # Note: For actual PDF testing, you would do:
    # files = {'pdf_file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}
    # response = requests.post(f"{BASE_URL}/api/generate-content", headers=headers, data=form_data, files=files)
    
    response = requests.post(f"{BASE_URL}/api/generate-content", headers=headers, data=form_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} cards from PDF content")
        return True
    else:
        print(f"❌ PDF generation failed: {response.json()}")
        return False

def test_focus_areas_feature(session_token):
    """Test focus areas functionality"""
    print("\n🎯 Testing focus areas feature...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    
    form_data = {
        'source_material': """
        Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience.
        Types include supervised learning, unsupervised learning, and reinforcement learning.
        Common algorithms: Linear Regression, Decision Trees, Neural Networks, K-Means Clustering.
        Applications: Image recognition, natural language processing, recommendation systems.
        """,
        'generation_type': 'information',
        'subject': 'Computer Science',
        'focus_areas': 'algorithms, types of learning',  # Specific focus
        'max_cards': '6'
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-content", headers=headers, data=form_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} focused cards")
        print("🎯 Content should focus on algorithms and learning types:")
        for i, card in enumerate(result['cards'][:3], 1):
            print(f"  {i}. {card['front']}")
        return True
    else:
        print(f"❌ Focus areas test failed: {response.json()}")
        return False

def test_optional_subject(session_token):
    """Test optional subject field"""
    print("\n📚 Testing optional subject field...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    
    form_data = {
        'source_material': """
        The water cycle involves evaporation, condensation, precipitation, and collection.
        Water evaporates from oceans, lakes, and rivers, forms clouds, and returns as rain or snow.
        """,
        'generation_type': 'flashcards',
        # Note: No subject specified (testing optional nature)
        'focus_areas': 'processes, stages',
        'max_cards': '4'
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-content", headers=headers, data=form_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} cards without subject specification")
        return True
    else:
        print(f"❌ Optional subject test failed: {response.json()}")
        return False

def test_generation_history(session_token):
    """Test content generation history"""
    print("\n📊 Testing generation history...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    
    # Get user info first
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get user info")
        return False
    
    user_id = response.json()['user']['id']
    
    # Get generation history
    response = requests.get(f"{BASE_URL}/api/users/{user_id}/content-generations", headers=headers)
    
    if response.status_code == 200:
        generations = response.json()['generations']
        print(f"✅ Retrieved {len(generations)} generation records")
        if generations:
            latest = generations[0]
            print(f"📋 Latest generation: {latest['generation_type']} - {latest['cards_generated']} cards")
            if latest.get('focus_areas'):
                print(f"🎯 Focus areas: {latest['focus_areas']}")
        return True
    else:
        print(f"❌ History retrieval failed: {response.json()}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced AI Generation Features")
    print("=" * 50)
    
    # Test authentication
    session_token = test_user_registration_and_login()
    if not session_token:
        print("❌ Authentication failed, cannot proceed with tests")
        return
    
    # Test various AI generation features
    tests = [
        test_text_based_generation,
        test_pdf_generation,
        test_focus_areas_feature,
        test_optional_subject,
        test_generation_history
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func(session_token):
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced AI generation is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        
    print("\n📝 Notes:")
    print("- PDF and image upload tests are simulated (no actual files uploaded)")
    print("- Actual AI generation requires OPENAI_API_KEY environment variable")
    print("- Focus areas and optional subjects are now supported")
    print("- Difficulty level has been removed as requested")

if __name__ == "__main__":
    main()