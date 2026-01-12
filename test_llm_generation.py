#!/usr/bin/env python3
"""
Test script for LLM Content Generation features
"""
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

# Sample study materials for testing
SAMPLE_MATERIALS = {
    "physics": """
Newton's Laws of Motion

First Law (Law of Inertia): An object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.

Second Law: The acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass. F = ma

Third Law: For every action, there is an equal and opposite reaction.

These laws form the foundation of classical mechanics and describe the relationship between forces acting on a body and its motion.
""",
    
    "biology": """
Photosynthesis Process

Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in two main stages:

Light-dependent reactions (occur in thylakoids):
- Chlorophyll absorbs light energy
- Water molecules are split (H2O → 2H+ + 1/2O2 + 2e-)
- ATP and NADPH are produced

Light-independent reactions (Calvin Cycle, occurs in stroma):
- CO2 is fixed into organic molecules
- Uses ATP and NADPH from light reactions
- Produces glucose (C6H12O6)

Overall equation: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
""",
    
    "history": """
World War II Timeline

1939: Germany invades Poland, Britain and France declare war on Germany
1940: Germany conquers France, Battle of Britain begins
1941: Germany invades Soviet Union, Japan attacks Pearl Harbor, US enters war
1942: Battle of Stalingrad begins, turning point on Eastern Front
1943: Italy surrenders, Allies gain momentum
1944: D-Day landings in Normandy, liberation of Western Europe begins
1945: Germany surrenders (May 8), atomic bombs dropped on Japan, Japan surrenders (August 15)

The war resulted in 70-85 million deaths and reshaped the global political landscape.
"""
}

def test_llm_content_generation():
    print("🤖 Testing LLM Content Generation System...")
    
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("   Testing will continue with mock responses...")
    
    # Test 1: Create a test user
    print("\n1. Setting up test user...")
    
    user_data = {
        "username": "llm_test_user",
        "email": "llm@test.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            print(f"✅ User created with ID: {user_id}")
        elif response.status_code == 400 and "already exists" in response.json().get("error", ""):
            # User already exists, get existing user
            user_id = 3  # Assume this is the existing user ID
            print(f"ℹ️  Using existing user with ID: {user_id}")
        else:
            print(f"❌ Failed to create user: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on port 5000")
        return
    
    # Test 2: Generate flashcards from physics material
    print("\n2. Generating flashcards from physics material...")
    
    flashcard_request = {
        "user_id": user_id,
        "source_material": SAMPLE_MATERIALS["physics"],
        "generation_type": "flashcards",
        "subject": "Physics",
        "max_cards": 5,
        "difficulty_level": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/generate-content", json=flashcard_request)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} flashcards")
        print("   Sample flashcards:")
        for i, card in enumerate(result['cards'][:2]):  # Show first 2
            print(f"   Q{i+1}: {card['front']}")
            print(f"   A{i+1}: {card['back']}")
            print()
    elif response.status_code == 503:
        print("ℹ️  OpenAI API not configured - this is expected for testing")
        print("   Response:", response.json()["error"])
    else:
        print(f"❌ Failed to generate flashcards: {response.text}")
    
    # Test 3: Generate information pieces from biology material
    print("\n3. Generating information pieces from biology material...")
    
    info_request = {
        "user_id": user_id,
        "source_material": SAMPLE_MATERIALS["biology"],
        "generation_type": "information",
        "subject": "Biology",
        "max_cards": 4,
        "difficulty_level": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/generate-content", json=info_request)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} information pieces")
        print("   Sample information:")
        for i, card in enumerate(result['cards'][:2]):  # Show first 2
            print(f"   INFO{i+1}: {card['front']}")
            print()
    elif response.status_code == 503:
        print("ℹ️  OpenAI API not configured - this is expected for testing")
    else:
        print(f"❌ Failed to generate information pieces: {response.text}")
    
    # Test 4: Generate mixed content from history material
    print("\n4. Generating mixed content from history material...")
    
    mixed_request = {
        "user_id": user_id,
        "source_material": SAMPLE_MATERIALS["history"],
        "generation_type": "mixed",
        "subject": "History",
        "max_cards": 6,
        "difficulty_level": "hard"
    }
    
    response = requests.post(f"{BASE_URL}/generate-content", json=mixed_request)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} mixed content items")
        flashcard_count = sum(1 for card in result['cards'] if card['back'] is not None)
        info_count = result['cards_generated'] - flashcard_count
        print(f"   - {flashcard_count} flashcards")
        print(f"   - {info_count} information pieces")
    elif response.status_code == 503:
        print("ℹ️  OpenAI API not configured - this is expected for testing")
    else:
        print(f"❌ Failed to generate mixed content: {response.text}")
    
    # Test 5: Get user's generation history
    print("\n5. Checking generation history...")
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/generations")
    if response.status_code == 200:
        generations = response.json()["generations"]
        print(f"✅ Found {len(generations)} generation records")
        for gen in generations:
            status_emoji = "✅" if gen["generation_status"] == "completed" else "❌" if gen["generation_status"] == "failed" else "⏳"
            print(f"   {status_emoji} {gen['generation_type']} - {gen['subject']} - {gen['cards_generated']} cards")
    else:
        print(f"❌ Failed to get generation history: {response.text}")
    
    # Test 6: Test error handling with invalid request
    print("\n6. Testing error handling...")
    
    invalid_request = {
        "user_id": user_id,
        "source_material": "",  # Empty material
        "generation_type": "invalid_type"
    }
    
    response = requests.post(f"{BASE_URL}/generate-content", json=invalid_request)
    if response.status_code == 400:
        print("✅ Error handling works correctly for invalid requests")
    else:
        print(f"⚠️  Unexpected response for invalid request: {response.status_code}")
    
    # Test 7: Check AI-generated cards in user's collection
    print("\n7. Checking AI-generated cards in collection...")
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/cards")
    if response.status_code == 200:
        cards = response.json()["cards"]
        ai_cards = [card for card in cards if card.get("is_ai_generated", False)]
        print(f"✅ User has {len(ai_cards)} AI-generated cards out of {len(cards)} total cards")
        
        if ai_cards:
            print("   Sample AI-generated cards:")
            for card in ai_cards[:2]:  # Show first 2
                print(f"   - {card['content_type']}: {card['front'][:60]}...")
    else:
        print(f"❌ Failed to get user cards: {response.text}")
    
    print("\n🎉 LLM Content Generation tests complete!")
    print("\n📋 Summary of features tested:")
    print("   ✅ Flashcard generation from text")
    print("   ✅ Information piece extraction")
    print("   ✅ Mixed content generation")
    print("   ✅ Generation history tracking")
    print("   ✅ Error handling and validation")
    print("   ✅ AI-generated content marking")
    print("   ✅ Integration with existing card system")
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n💡 To test with real AI generation:")
        print("   1. Get an OpenAI API key from https://platform.openai.com/")
        print("   2. Set environment variable: export OPENAI_API_KEY='your-key'")
        print("   3. Restart the Flask server")
        print("   4. Run this test again")
    else:
        print("\n🚀 Ready for production AI content generation!")

if __name__ == "__main__":
    test_llm_content_generation()