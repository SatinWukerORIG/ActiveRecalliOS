"""
Enhanced Live Activity Service for Active Recall
Displays study content when phone is unlocked
"""
import os
import jwt
import time
import httpx
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.models import User, Card
from app.config import Config
from app import db

class LiveActivityService:
    """Enhanced service for managing iOS Live Activities with study content"""
    
    def __init__(self):
        self.config = Config()
    
    def _create_apns_token(self):
        """Generate JWT token for APNs authentication"""
        if not os.path.exists(self.config.APNS_KEY_PATH):
            raise Exception("APNs key file not found")
            
        with open(self.config.APNS_KEY_PATH, "r") as f:
            secret = f.read()

        token = jwt.encode(
            {
                "iss": self.config.APNS_TEAM_ID,
                "iat": time.time(),
            },
            secret,
            algorithm="ES256",
            headers={"alg": "ES256", "kid": self.config.APNS_AUTH_KEY_ID},
        )
        return token
    
    async def start_live_activity(self, user_id: int) -> Dict[str, Any]:
        """Start a Live Activity for a user with initial study content"""
        user = User.query.get(user_id)
        if not user or not user.live_activity_enabled:
            return {"success": False, "error": "User not found or Live Activities disabled"}
        
        # Get a random study card for initial display
        study_card = self._get_random_study_card(user)
        if not study_card:
            return {"success": False, "error": "No study content available"}
        
        # Create Live Activity payload
        payload = self._create_live_activity_payload(study_card, "start")
        
        try:
            # Send to APNs
            response_code = await self._send_live_activity_update(
                user.active_activity_token or user.device_token,
                payload
            )
            
            if response_code == 200:
                # Update user's last activity time
                user.last_notification_time = datetime.utcnow()
                db.session.commit()
                
                return {
                    "success": True,
                    "card_id": study_card.id,
                    "content_type": study_card.content_type,
                    "message": "Live Activity started with study content"
                }
            else:
                return {"success": False, "error": f"APNs request failed: {response_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_live_activity_on_unlock(self, user_id: int) -> Dict[str, Any]:
        """Update Live Activity with new study content when phone is unlocked"""
        user = User.query.get(user_id)
        if not user or not user.live_activity_enabled:
            return {"success": False, "error": "User not found or Live Activities disabled"}
        
        # Check if enough time has passed since last update
        if not self._should_update_content(user):
            return {"success": False, "error": "Too soon for content update"}
        
        # Get a new random study card
        study_card = self._get_random_study_card(user)
        if not study_card:
            return {"success": False, "error": "No study content available"}
        
        # Create update payload
        payload = self._create_live_activity_payload(study_card, "update")
        
        try:
            response_code = await self._send_live_activity_update(
                user.active_activity_token or user.device_token,
                payload
            )
            
            if response_code == 200:
                # Update user's last activity time
                user.last_notification_time = datetime.utcnow()
                db.session.commit()
                
                return {
                    "success": True,
                    "card_id": study_card.id,
                    "content_type": study_card.content_type,
                    "content": study_card.front,
                    "message": "Live Activity updated with new study content"
                }
            else:
                return {"success": False, "error": f"APNs request failed: {response_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def end_live_activity(self, user_id: int) -> Dict[str, Any]:
        """End the Live Activity for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        payload = {
            "aps": {
                "timestamp": int(time.time()),
                "event": "end",
                "dismissal-date": int(time.time())
            }
        }
        
        try:
            response_code = await self._send_live_activity_update(
                user.active_activity_token or user.device_token,
                payload
            )
            
            return {
                "success": response_code == 200,
                "message": "Live Activity ended" if response_code == 200 else f"Failed to end: {response_code}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_random_study_card(self, user: User) -> Optional[Card]:
        """Get a random study card based on user's notification preferences"""
        # Base query for cards
        query = Card.query.filter(Card.user_id == user.id)
        
        # Filter by selected folders if specified
        if user.recall_folders:
            folder_ids = [int(fid.strip()) for fid in user.recall_folders.split(',') if fid.strip().isdigit()]
            if folder_ids:
                query = query.filter(Card.folder_id.in_(folder_ids))
        
        # Get all eligible cards
        cards = query.all()
        
        if not cards:
            return None
        
        # Prioritize due cards, but include others for variety
        due_cards = [card for card in cards if card.is_due_for_review()]
        
        if due_cards and random.random() < 0.7:  # 70% chance to show due cards
            return random.choice(due_cards)
        else:
            return random.choice(cards)
    
    def _should_update_content(self, user: User) -> bool:
        """Check if enough time has passed to update Live Activity content"""
        if not user.last_notification_time:
            return True
        
        # Minimum 5 minutes between updates to avoid spam
        min_interval = timedelta(minutes=5)
        time_since_last = datetime.utcnow() - user.last_notification_time
        
        return time_since_last >= min_interval
    
    def _create_live_activity_payload(self, card: Card, event_type: str = "update") -> Dict[str, Any]:
        """Create Live Activity payload with study content"""
        
        # Format content based on card type
        if card.content_type == 'flashcard':
            content_state = {
                "cardId": card.id,
                "cardType": "flashcard",
                "question": card.front,
                "answer": card.back,
                "subject": card.subject or "Study",
                "showAnswer": False,  # Initially hide answer
                "isOverdue": card.is_due_for_review(),
                "folderName": card.folder.name if card.folder else None,
                "lastUpdated": int(time.time())
            }
        else:  # information piece
            content_state = {
                "cardId": card.id,
                "cardType": "information",
                "information": card.front,
                "subject": card.subject or "Knowledge",
                "showAnswer": True,  # Always show for info pieces
                "isOverdue": card.is_due_for_review(),
                "folderName": card.folder.name if card.folder else None,
                "lastUpdated": int(time.time())
            }
        
        payload = {
            "aps": {
                "timestamp": int(time.time()),
                "event": event_type,
                "content-state": content_state,
                "alert": {
                    "title": "🧠 Active Recall",
                    "body": f"New {card.content_type}: {card.front[:50]}..." if len(card.front) > 50 else card.front
                } if event_type == "start" else None
            }
        }
        
        return payload
    
    async def _send_live_activity_update(self, activity_token: str, payload: Dict[str, Any]) -> int:
        """Send Live Activity update to APNs"""
        try:
            token = self._create_apns_token()
            url = f"https://api.development.push.apple.com/3/device/{activity_token}"
            
            headers = {
                "apns-topic": f"{self.config.BUNDLE_ID}.push-type.liveactivity",
                "authorization": f"bearer {token}",
                "apns-push-type": "liveactivity",
                "apns-priority": "10"
            }

            async with httpx.AsyncClient(http2=True) as client:
                response = await client.post(url, headers=headers, json=payload)
                return response.status_code
                
        except Exception as e:
            print(f"Failed to send Live Activity update: {e}")
            return 500
    
    # Webhook endpoint for iOS to call when phone is unlocked
    async def handle_unlock_webhook(self, user_id: int, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle webhook from iOS when phone is unlocked"""
        print(f"Phone unlock detected for user {user_id}")
        
        # Update Live Activity with new content
        result = await self.update_live_activity_on_unlock(user_id)
        
        # Log the interaction for analytics
        if result.get("success"):
            print(f"Live Activity updated for user {user_id} with card {result.get('card_id')}")
        
        return result
    
    def get_user_live_activity_status(self, user_id: int) -> Dict[str, Any]:
        """Get current Live Activity status for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        return {
            "user_id": user_id,
            "live_activity_enabled": user.live_activity_enabled,
            "has_activity_token": bool(user.active_activity_token),
            "last_update": user.last_notification_time.isoformat() if user.last_notification_time else None,
            "recall_folders": user.recall_folders,
            "available_cards": Card.query.filter(Card.user_id == user_id).count()
        }

# Singleton instance
live_activity_service = LiveActivityService()