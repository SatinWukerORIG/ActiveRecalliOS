"""
Notification Service for push notifications and scheduling
"""
import os
import jwt
import time
import httpx
import schedule
import threading
from datetime import datetime, time as dt_time
from app.models import User
from app.services.spaced_repetition import SpacedRepetitionService
from app.config import Config

class NotificationService:
    """Service for managing push notifications and smart scheduling"""
    
    def __init__(self):
        self.config = Config()
        self.scheduler_running = False
    
    def start_scheduler(self):
        """Start the notification scheduler in a background thread"""
        if self.scheduler_running:
            return
            
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Schedule notifications check every 5 minutes (will respect individual user frequencies)
        schedule.every(5).minutes.do(self._send_scheduled_notifications)
        
        self.scheduler_running = True
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("Notification scheduler started")
    
    def stop_scheduler(self):
        """Stop the notification scheduler"""
        self.scheduler_running = False
        schedule.clear()
    
    def _send_scheduled_notifications(self):
        """Send notifications to users with due cards"""
        try:
            # Get users with recall notifications enabled
            users = User.query.filter(
                User.device_token.isnot(None),
                User.recall_enabled == True
            ).all()
            
            for user in users:
                if self._should_send_notification(user) and self._is_time_for_notification(user):
                    # Get cards from selected folders or all folders
                    due_cards = self._get_recall_cards(user)
                    if due_cards:
                        # Pick a random card to show in notification
                        import random
                        selected_card = random.choice(due_cards)
                        self._send_card_notification(user, selected_card)
                        self._update_last_notification_time(user)
                        
        except Exception as e:
            print(f"Error in scheduled notifications: {e}")
    
    def _get_recall_cards(self, user):
        """Get cards for recall based on user's folder selection"""
        from app.models import Card
        
        # Base query for due cards
        query = Card.query.filter(
            Card.user_id == user.id,
            Card.next_review <= datetime.utcnow()
        )
        
        # Filter by selected folders if specified
        if user.recall_folders:
            folder_ids = [int(fid.strip()) for fid in user.recall_folders.split(',') if fid.strip().isdigit()]
            if folder_ids:
                query = query.filter(Card.folder_id.in_(folder_ids))
        
        return query.limit(10).all()  # Limit to prevent too many options
    
    def _is_time_for_notification(self, user):
        """Check if enough time has passed since last notification"""
        from datetime import datetime, timedelta
        
        # If no last notification time recorded, it's time to send
        if not hasattr(user, 'last_notification_time') or not user.last_notification_time:
            return True
        
        # Check if frequency interval has passed
        frequency_minutes = user.recall_frequency_minutes or 30
        time_since_last = datetime.utcnow() - user.last_notification_time
        
        return time_since_last >= timedelta(minutes=frequency_minutes)
    
    def _update_last_notification_time(self, user):
        """Update the last notification time for user"""
        from datetime import datetime
        from app import db
        
        user.last_notification_time = datetime.utcnow()
        db.session.commit()
    
    def _should_send_notification(self, user):
        """Check if we should send a notification to this user"""
        from datetime import datetime
        
        # Check if recalls are enabled
        if not user.recall_enabled:
            return False
        
        # Check if recalls are paused
        if user.recall_paused:
            return False
            
        # Check focus mode
        if user.focus_mode:
            return False
        
        # Check time range
        current_time = datetime.now().time()
        if user.recall_start_time and user.recall_end_time:
            if not (user.recall_start_time <= current_time <= user.recall_end_time):
                return False
        
        # Check day of week
        if user.recall_days_of_week:
            current_day = str(datetime.now().isoweekday())  # 1=Monday, 7=Sunday
            active_days = user.recall_days_of_week.split(',')
            if current_day not in active_days:
                return False
        
        # Check sleep schedule
        if user.sleep_start and user.sleep_end:
            if self._is_sleep_time(current_time, user.sleep_start, user.sleep_end):
                return False
        
        return True
    
    def _is_sleep_time(self, current_time, sleep_start, sleep_end):
        """Check if current time is within sleep schedule"""
        if sleep_start <= sleep_end:
            # Same day sleep schedule (e.g., 22:00 to 06:00)
            return sleep_start <= current_time <= sleep_end
        else:
            # Overnight sleep schedule (e.g., 22:00 to 06:00 next day)
            return current_time >= sleep_start or current_time <= sleep_end
    
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
            algorithm=self.config.ALGORITHM,
            headers={"alg": self.config.ALGORITHM, "kid": self.config.APNS_AUTH_KEY_ID},
        )
        return token
    
    async def _send_push_notification(self, device_token, payload, push_type="alert", activity_token=None):
        """Send push notification via APNs"""
        try:
            token = self._create_apns_token()
            url = f"https://api.development.push.apple.com/3/device/{device_token if not activity_token else activity_token}"
            
            headers = {
                "apns-topic": self.config.BUNDLE_ID if push_type == "alert" else f"{self.config.BUNDLE_ID}.push-type.liveactivity",
                "authorization": f"bearer {token}",
                "apns-push-type": push_type,
                "apns-priority": "10"
            }

            async with httpx.AsyncClient(http2=True) as client:
                response = await client.post(url, headers=headers, json=payload)
                return response.status_code
                
        except Exception as e:
            print(f"Failed to send push notification: {e}")
            return 500
    
    def _send_card_notification(self, user, card):
        """Send notification with actual card content"""
        if not user.device_token:
            return
        
        # Format card content for notification
        if card.content_type == 'flashcard':
            title = "🧠 Quick Recall"
            body = f"Q: {card.front}"
            # For flashcards, we could show the question and let them think, then reveal answer
            subtitle = f"Tap to see answer"
        else:  # information piece
            title = "💡 Remember This"
            body = card.front
            subtitle = f"Subject: {card.subject}" if card.subject else "Key Information"
        
        # Truncate long content for notification
        if len(body) > 100:
            body = body[:97] + "..."
        
        payload = {
            "aps": {
                "alert": {
                    "title": title,
                    "subtitle": subtitle,
                    "body": body
                },
                "badge": 1,
                "sound": "default",
                "category": "RECALL_CARD"  # For custom actions
            },
            "card_id": card.id,
            "content_type": card.content_type,
            "card_back": card.back if card.content_type == 'flashcard' else None
        }
        
        # Send Live Activity update if enabled
        if user.live_activity_enabled and user.active_activity_token:
            self._send_live_activity_update(user, card)
        
        # Note: In a real app, you'd use asyncio.run() or run this in an async context
        # For now, we'll just log the notification
        print(f"Would send card notification to {user.username}:")
        print(f"  Title: {title}")
        print(f"  Body: {body}")
        print(f"  Card ID: {card.id}")
    
    def _send_live_activity_update(self, user, card):
        """Send Live Activity update with card content"""
        if not user.active_activity_token:
            return
        
        # Format content for Live Activity
        if card.content_type == 'flashcard':
            content_state = {
                "question": card.front,
                "answer": card.back,
                "cardType": "flashcard",
                "subject": card.subject or "Study",
                "showAnswer": False  # Initially hide answer
            }
        else:
            content_state = {
                "information": card.front,
                "cardType": "information", 
                "subject": card.subject or "Knowledge",
                "showAnswer": True  # Always show for info pieces
            }
        
        payload = {
            "aps": {
                "timestamp": int(time.time()),
                "event": "update",
                "content-state": content_state
            }
        }
        
        print(f"Would send Live Activity update to {user.username}:")
        print(f"  Content: {content_state}")
    
    def _send_study_reminder(self, user, due_count):
        """Legacy method - kept for compatibility"""
        # This is now replaced by _send_card_notification
        pass
    
    def register_device_token(self, user_id, device_token):
        """Register device token for push notifications"""
        user = User.query.get(user_id)
        if user:
            user.device_token = device_token
            from app import db
            db.session.commit()
            return True
        return False
    
    def register_live_activity_token(self, user_id, activity_token):
        """Register Live Activity token"""
        user = User.query.get(user_id)
        if user:
            user.active_activity_token = activity_token
            from app import db
            db.session.commit()
            return True
        return False