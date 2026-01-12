#!/usr/bin/env python3
"""
Comprehensive test for Live Activity and notification settings functionality
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "testuser_live",
    "email": "test_live@example.com",
    "password": "testpass123",
    "first_name": "Live",
    "last_name": "Tester"
}

class LiveActivityTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.session_token = None
    
    def register_and_login(self):
        """Register and login test user"""
        print("🔐 Registering and logging in test user...")
        
        # Register
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if response.status_code in [200, 201]:
            print("✅ User registered successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️ User already exists, proceeding to login")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
        
        # Login
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            self.session_token = result.get('session_token')
            self.user_id = result.get('user', {}).get('id')
            
            # Set session token in headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.session_token}'
            })
            
            print(f"✅ Login successful - User ID: {self.user_id}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def test_device_token_registration(self):
        """Test device token registration"""
        print("\n📱 Testing device token registration...")
        
        test_device_token = "test_device_token_12345"
        
        response = self.session.post(
            f"{BASE_URL}/api/users/{self.user_id}/register-device",
            json={"device_token": test_device_token}
        )
        
        if response.status_code == 200:
            print("✅ Device token registered successfully")
            return True
        else:
            print(f"❌ Device token registration failed: {response.text}")
            return False
    
    def test_live_activity_token_registration(self):
        """Test Live Activity token registration"""
        print("\n🔴 Testing Live Activity token registration...")
        
        test_activity_token = "test_live_activity_token_67890"
        
        response = self.session.post(
            f"{BASE_URL}/api/users/{self.user_id}/register-live-activity",
            json={"activity_token": test_activity_token}
        )
        
        if response.status_code == 200:
            print("✅ Live Activity token registered successfully")
            return True
        else:
            print(f"❌ Live Activity token registration failed: {response.text}")
            return False
    
    def create_test_cards(self):
        """Create test cards for Live Activity testing"""
        print("\n📚 Creating test cards...")
        
        test_cards = [
            {
                "front": "What is the capital of France?",
                "back": "Paris",
                "content_type": "flashcard",
                "subject": "Geography"
            },
            {
                "front": "E = mc²",
                "back": "Einstein's mass-energy equivalence formula",
                "content_type": "information",
                "subject": "Physics"
            },
            {
                "front": "Bonjour",
                "back": "Hello (French)",
                "content_type": "flashcard",
                "subject": "French"
            }
        ]
        
        created_cards = []
        for card_data in test_cards:
            response = self.session.post(f"{BASE_URL}/api/cards", json=card_data)
            if response.status_code in [200, 201]:
                created_cards.append(response.json())
                print(f"✅ Created card: {card_data['front'][:30]}...")
            else:
                print(f"❌ Failed to create card: {response.text}")
        
        return created_cards
    
    def test_notification_settings_update(self):
        """Test updating notification settings"""
        print("\n⚙️ Testing notification settings update...")
        
        settings = {
            "recall_enabled": True,
            "recall_frequency_minutes": 15,
            "recall_start_time": "09:00",
            "recall_end_time": "21:00",
            "max_daily_recalls": 25,
            "recall_days_of_week": "1,2,3,4,5",
            "live_activity_enabled": True,
            "show_card_preview": True,
            "show_progress_updates": True,
            "focus_mode": False,
            "sleep_start": "23:00",
            "sleep_end": "07:00"
        }
        
        response = self.session.put(f"{BASE_URL}/api/auth/profile", json=settings)
        
        if response.status_code == 200:
            print("✅ Notification settings updated successfully")
            return True
        else:
            print(f"❌ Failed to update settings: {response.text}")
            return False
    
    def test_live_activity_endpoints(self):
        """Test Live Activity API endpoints"""
        print("\n🎯 Testing Live Activity endpoints...")
        
        # Test start study session
        print("Testing start study session...")
        response = self.session.post(f"{BASE_URL}/api/live-activity/start-session")
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"✅ Study session started: {session_id}")
            
            # Test update progress
            print("Testing progress update...")
            update_data = {
                "session_id": session_id,
                "current_card_index": 1,
                "cards_reviewed": 1,
                "total_cards": 3
            }
            response = self.session.post(f"{BASE_URL}/api/live-activity/update-progress", json=update_data)
            if response.status_code == 200:
                print("✅ Progress updated successfully")
            else:
                print(f"❌ Progress update failed: {response.text}")
            
            # Test end session
            print("Testing end session...")
            end_data = {
                "session_id": session_id,
                "cards_reviewed": 3,
                "session_duration": 180  # 3 minutes
            }
            response = self.session.post(f"{BASE_URL}/api/live-activity/end-session", json=end_data)
            if response.status_code == 200:
                print("✅ Session ended successfully")
            else:
                print(f"❌ End session failed: {response.text}")
                
        else:
            print(f"❌ Start session failed: {response.text}")
        
        # Test recall reminder
        print("Testing recall reminder...")
        response = self.session.post(f"{BASE_URL}/api/live-activity/recall-reminder")
        if response.status_code == 200:
            print("✅ Recall reminder sent successfully")
        else:
            print(f"❌ Recall reminder failed: {response.text}")
        
        # Test daily progress
        print("Testing daily progress...")
        response = self.session.post(f"{BASE_URL}/api/live-activity/daily-progress")
        if response.status_code == 200:
            print("✅ Daily progress sent successfully")
        else:
            print(f"❌ Daily progress failed: {response.text}")
        
        # Test Live Activity test
        print("Testing Live Activity test...")
        response = self.session.post(f"{BASE_URL}/api/live-activity/test")
        if response.status_code == 200:
            print("✅ Test Live Activity sent successfully")
        else:
            print(f"❌ Test Live Activity failed: {response.text}")
    
    def test_notification_status_and_controls(self):
        """Test notification status and control endpoints"""
        print("\n📊 Testing notification status and controls...")
        
        # Test status
        response = self.session.get(f"{BASE_URL}/api/notifications/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status retrieved: {json.dumps(status, indent=2)}")
        else:
            print(f"❌ Status retrieval failed: {response.text}")
        
        # Test pause
        response = self.session.post(f"{BASE_URL}/api/notifications/pause", json={"duration_hours": 1})
        if response.status_code == 200:
            print("✅ Notifications paused successfully")
        else:
            print(f"❌ Pause failed: {response.text}")
        
        # Test resume
        response = self.session.post(f"{BASE_URL}/api/notifications/resume")
        if response.status_code == 200:
            print("✅ Notifications resumed successfully")
        else:
            print(f"❌ Resume failed: {response.text}")
        
        # Test recall test
        response = self.session.post(f"{BASE_URL}/api/notifications/test-recall")
        if response.status_code == 200:
            print("✅ Test recall sent successfully")
        else:
            print(f"❌ Test recall failed: {response.text}")
    
    def test_web_interface(self):
        """Test web interface accessibility"""
        print("\n🌐 Testing web interface...")
        
        # Test notification settings page
        response = self.session.get(f"{BASE_URL}/notifications")
        if response.status_code == 200:
            print("✅ Notification settings page accessible")
        else:
            print(f"❌ Notification settings page failed: {response.status_code}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Live Activity and Notification Settings Tests")
        print("=" * 60)
        
        if not self.register_and_login():
            return False
        
        # Run all test methods
        tests = [
            self.test_device_token_registration,
            self.test_live_activity_token_registration,
            self.create_test_cards,
            self.test_notification_settings_update,
            self.test_live_activity_endpoints,
            self.test_notification_status_and_controls,
            self.test_web_interface
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 60)
        print(f"🏁 Tests completed: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! Live Activity and notification system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main test function"""
    tester = LiveActivityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ Live Activity and notification system is ready for iOS integration!")
        print("\nNext steps:")
        print("1. Update iOS app to register Live Activity tokens")
        print("2. Test with real iOS device")
        print("3. Configure APNs with production certificates")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")

if __name__ == "__main__":
    main()