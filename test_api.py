#!/usr/bin/env python3
"""
Simple test script for Active Recall API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_api():
    print("🧪 Testing Active Recall API...")
    
    # Test 1: Create a user
    print("\n1. Creating a user...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "notification_frequency": 45
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            print(f"✅ User created with ID: {user_id}")
        else:
            print(f"❌ Failed to create user: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on port 5000")
        return
    
    # Test 2: Add a flashcard
    print("\n2. Adding a flashcard...")
    card_data = {
        "user_id": user_id,
        "content_type": "flashcard",
        "front": "What is the capital of France?",
        "back": "Paris",
        "subject": "Geography"
    }
    
    response = requests.post(f"{BASE_URL}/cards", json=card_data)
    if response.status_code == 201:
        card_id = response.json()["card_id"]
        print(f"✅ Flashcard created with ID: {card_id}")
    else:
        print(f"❌ Failed to create flashcard: {response.text}")
        return
    
    # Test 3: Add an information piece
    print("\n3. Adding an information piece...")
    info_data = {
        "user_id": user_id,
        "content_type": "information",
        "front": "E = mc²",
        "subject": "Physics",
        "tags": ["formula", "einstein", "relativity"]
    }
    
    response = requests.post(f"{BASE_URL}/cards", json=info_data)
    if response.status_code == 201:
        info_id = response.json()["card_id"]
        print(f"✅ Information piece created with ID: {info_id}")
    else:
        print(f"❌ Failed to create information piece: {response.text}")
    
    # Test 4: Get user's cards
    print("\n4. Retrieving user's cards...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/cards")
    if response.status_code == 200:
        cards = response.json()["cards"]
        print(f"✅ Retrieved {len(cards)} cards")
        for card in cards:
            print(f"   - {card['content_type']}: {card['front'][:50]}...")
    else:
        print(f"❌ Failed to get cards: {response.text}")
    
    # Test 5: Get due cards
    print("\n5. Getting due cards...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/cards/due")
    if response.status_code == 200:
        due_cards = response.json()["due_cards"]
        print(f"✅ Found {len(due_cards)} cards due for review")
    else:
        print(f"❌ Failed to get due cards: {response.text}")
    
    # Test 6: Review a card
    print("\n6. Reviewing a card...")
    review_data = {"quality": 4}  # Good recall
    response = requests.post(f"{BASE_URL}/review/{card_id}", json=review_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Card reviewed. Next review: {result['next_review']}")
    else:
        print(f"❌ Failed to review card: {response.text}")
    
    # Test 7: Get user stats
    print("\n7. Getting user statistics...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ User stats: {stats}")
    else:
        print(f"❌ Failed to get stats: {response.text}")
    
    print("\n🎉 API testing complete!")

if __name__ == "__main__":
    test_api()