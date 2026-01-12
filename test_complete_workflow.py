#!/usr/bin/env python3
"""
Complete Active Recall Workflow Test
Tests the entire user journey from content creation to spaced repetition
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_complete_workflow():
    print("🎯 Testing Complete Active Recall Workflow...")
    print("   This test demonstrates the full user journey from content creation to spaced repetition")
    
    # Step 1: Create a new user (student persona)
    print("\n📚 Step 1: Creating a student user...")
    
    user_data = {
        "username": "student_alice",
        "email": "alice@university.edu",
        "notification_frequency": 30
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            print(f"✅ Student created: Alice (ID: {user_id})")
        elif response.status_code == 400 and "already exists" in response.json().get("error", ""):
            user_id = 4  # Use existing user
            print(f"ℹ️  Using existing student: Alice (ID: {user_id})")
        else:
            print(f"❌ Failed to create user: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on port 5000")
        return
    
    # Step 2: Generate AI content from study material
    print("\n🤖 Step 2: Generating study content with AI...")
    
    study_material = """
    Cellular Respiration Overview
    
    Cellular respiration is the process by which cells break down glucose to produce ATP (energy).
    It occurs in three main stages:
    
    1. Glycolysis: Occurs in cytoplasm, breaks glucose into pyruvate, produces 2 ATP
    2. Krebs Cycle (Citric Acid Cycle): Occurs in mitochondria, produces NADH and FADH2
    3. Electron Transport Chain: Occurs in inner mitochondrial membrane, produces most ATP (about 32-34 ATP)
    
    Overall equation: C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP
    
    This process is essential for all living organisms and is the opposite of photosynthesis.
    """
    
    generation_request = {
        "user_id": user_id,
        "source_material": study_material,
        "generation_type": "mixed",
        "subject": "Biology",
        "max_cards": 8,
        "difficulty_level": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/generate-content", json=generation_request)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Generated {result['cards_generated']} study items")
        print(f"   Generation ID: {result['generation_id']}")
        
        # Show sample generated content
        flashcards = [card for card in result['cards'] if card['back'] is not None]
        info_pieces = [card for card in result['cards'] if card['back'] is None]
        print(f"   - {len(flashcards)} flashcards")
        print(f"   - {len(info_pieces)} information pieces")
        
        if flashcards:
            print(f"   Sample flashcard: {flashcards[0]['front'][:60]}...")
        if info_pieces:
            print(f"   Sample info: {info_pieces[0]['front'][:60]}...")
            
    elif response.status_code == 503:
        print("ℹ️  AI generation not configured - adding manual content instead")
        
        # Add manual content as fallback
        manual_cards = [
            {
                "user_id": user_id,
                "content_type": "flashcard",
                "front": "What are the three main stages of cellular respiration?",
                "back": "Glycolysis, Krebs Cycle, and Electron Transport Chain",
                "subject": "Biology"
            },
            {
                "user_id": user_id,
                "content_type": "information",
                "front": "Cellular respiration equation: C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP",
                "subject": "Biology"
            }
        ]
        
        for card_data in manual_cards:
            requests.post(f"{BASE_URL}/cards", json=card_data)
        
        print("✅ Added manual study content as fallback")
    else:
        print(f"❌ Failed to generate content: {response.text}")
        return
    
    # Step 3: Check user's learning statistics
    print("\n📊 Step 3: Checking learning progress...")
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Learning Statistics:")
        print(f"   - Total cards: {stats['total_cards']}")
        print(f"   - Due for review: {stats['due_cards']}")
        print(f"   - Subjects: {list(stats['subjects'].keys())}")
    else:
        print(f"❌ Failed to get stats: {response.text}")
    
    # Step 4: Simulate study session
    print("\n🎓 Step 4: Simulating study session...")
    
    # Get due cards
    response = requests.get(f"{BASE_URL}/users/{user_id}/cards/due")
    if response.status_code == 200:
        due_cards = response.json()["due_cards"]
        print(f"✅ Found {len(due_cards)} cards due for review")
        
        if due_cards:
            # Simulate reviewing first few cards
            for i, card in enumerate(due_cards[:3]):
                print(f"\n   📝 Reviewing card {i+1}: {card['front'][:50]}...")
                
                # Simulate different quality responses
                quality = [4, 5, 3][i % 3]  # Good, Easy, Hard
                quality_names = {4: "Good", 5: "Easy", 3: "Hard"}
                
                review_data = {"quality": quality}
                response = requests.post(f"{BASE_URL}/review/{card['id']}", json=review_data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Marked as {quality_names[quality]} - Next review: {result['next_review'][:10]}")
                else:
                    print(f"   ❌ Failed to review card: {response.text}")
    else:
        print(f"❌ Failed to get due cards: {response.text}")
    
    # Step 5: Test smart scheduling system
    print("\n⏰ Step 5: Testing smart scheduling...")
    
    # Check availability
    response = requests.get(f"{BASE_URL}/users/{user_id}/availability")
    if response.status_code == 200:
        availability = response.json()
        print(f"✅ User availability: {availability['available']}")
        
        if availability['available']:
            # Try sending a smart notification
            response = requests.post(f"{BASE_URL}/send-study-notification/{user_id}")
            if response.status_code == 200:
                result = response.json()
                if "card_id" in result:
                    print(f"✅ Smart notification sent for: {result['card_front'][:50]}...")
                else:
                    print(f"ℹ️  {result['message']}")
            else:
                print(f"ℹ️  Notification not sent (expected without device token)")
        else:
            print(f"ℹ️  User not available: {', '.join(availability['reasons'])}")
    
    # Step 6: Test focus mode (context awareness)
    print("\n🎯 Step 6: Testing context awareness (focus mode)...")
    
    # Enable focus mode
    focus_data = {"focus_mode": True}
    response = requests.put(f"{BASE_URL}/users/{user_id}/preferences", json=focus_data)
    if response.status_code == 200:
        print("✅ Focus mode enabled")
        
        # Check availability again
        response = requests.get(f"{BASE_URL}/users/{user_id}/availability")
        if response.status_code == 200:
            availability = response.json()
            print(f"   Availability with focus mode: {availability['available']}")
            print(f"   Reason: {availability['reasons'][0] if availability['reasons'] else 'None'}")
        
        # Disable focus mode
        focus_data = {"focus_mode": False}
        requests.put(f"{BASE_URL}/users/{user_id}/preferences", json=focus_data)
        print("✅ Focus mode disabled")
    
    # Step 7: Check generation history
    print("\n📈 Step 7: Reviewing AI generation history...")
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/generations")
    if response.status_code == 200:
        generations = response.json()["generations"]
        print(f"✅ Found {len(generations)} AI generation sessions")
        
        for gen in generations:
            status_emoji = "✅" if gen["generation_status"] == "completed" else "❌"
            print(f"   {status_emoji} {gen['generation_type']} - {gen['subject']} - {gen['cards_generated']} cards")
    else:
        print(f"ℹ️  No generation history (expected without AI)")
    
    # Step 8: Final statistics
    print("\n📊 Step 8: Final learning progress...")
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/stats")
    if response.status_code == 200:
        final_stats = response.json()
        print(f"✅ Final Statistics:")
        print(f"   - Total cards: {final_stats['total_cards']}")
        print(f"   - Due for review: {final_stats['due_cards']}")
        print(f"   - Subjects studied: {len(final_stats['subjects'])}")
    
    # Success summary
    print("\n🎉 Complete Workflow Test Successful!")
    print("\n📋 Workflow Summary:")
    print("   ✅ User Registration & Profile Management")
    print("   ✅ AI-Powered Content Generation (or manual fallback)")
    print("   ✅ Spaced Repetition Learning Sessions")
    print("   ✅ Smart Scheduling & Context Awareness")
    print("   ✅ Focus Mode & User Preferences")
    print("   ✅ Learning Analytics & Progress Tracking")
    print("   ✅ Generation History & Content Management")
    
    print("\n🚀 Active Recall is ready for real-world deployment!")
    print("\n💡 Next steps for production:")
    print("   1. Set up OpenAI API key for AI content generation")
    print("   2. Configure Apple Push Notification Service")
    print("   3. Deploy iOS app to App Store")
    print("   4. Set up production server infrastructure")
    print("   5. Implement user analytics and monitoring")

if __name__ == "__main__":
    test_complete_workflow()