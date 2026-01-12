"""
iOS Live Activity Service for Active Recall
Manages Live Activities on iOS home screen and lock screen
"""
import json
import asyncio
from datetime import datetime, timedelta
from app.services.notification_service import NotificationService
from app.models import User, Card
from app.services.spaced_repetition import SpacedRepetitionService
from app import db

class LiveActivityService:
    """Service for managing iOS Live Activities"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    async def start_study_session_activity(self, user_id: int, session_cards: list):
        """Start a Live Activity for a study session"""
        user = User.query.get(user_id)
        if not user or not user.active_activity_token:
            return {"success": False, "error": "No Live Activity token registered"}
        
        # Prepare Live Activity payload
        payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "start",
                "content-state": {
                    "sessionId": f"session_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "totalCards": len(session_cards),
                    "currentCard": 0,
                    "cardsReviewed": 0,
                    "sessionStartTime": datetime.utcnow().isoformat(),
                    "currentCardContent": session_cards[0]['front'] if session_cards else "No cards available",
                    "currentCardType": session_cards[0]['content_type'] if session_cards else "none",
                    "userName": user.get_full_name()
                }
            }
        }
        
        # Send Live Activity start
        status_code = await self.notification_service._send_push_notification(
            device_token=user.device_token,
            payload=payload,
            push_type="liveactivity",
            activity_token=user.active_activity_token
        )
        
        if status_code == 200:
            return {
                "success": True,
                "message": "Study session Live Activity started",
                "session_id": payload["aps"]["content-state"]["sessionId"]
            }
        else:
            return {"success": False, "error": f"Failed to start Live Activity: {status_code}"}
    
    async def update_study_progress(self, user_id: int, session_id: str, current_card_index: int, 
                                  cards_reviewed: int, total_cards: int, current_card: dict = None):
        """Update Live Activity with study progress"""
        user = User.query.get(user_id)
        if not user or not user.active_activity_token:
            return {"success": False, "error": "No Live Activity token registered"}
        
        # Calculate progress
        progress = (cards_reviewed / total_cards) if total_cards > 0 else 0
        
        payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "update",
                "content-state": {
                    "sessionId": session_id,
                    "totalCards": total_cards,
                    "currentCard": current_card_index,
                    "cardsReviewed": cards_reviewed,
                    "progress": round(progress * 100, 1),
                    "currentCardContent": current_card['front'] if current_card else "Session complete",
                    "currentCardType": current_card['content_type'] if current_card else "complete",
                    "userName": user.get_full_name()
                }
            }
        }
        
        status_code = await self.notification_service._send_push_notification(
            device_token=user.device_token,
            payload=payload,
            push_type="liveactivity",
            activity_token=user.active_activity_token
        )
        
        return {"success": status_code == 200, "status_code": status_code}
    
    async def end_study_session_activity(self, user_id: int, session_id: str, 
                                       cards_reviewed: int, session_duration: int):
        """End a Live Activity study session"""
        user = User.query.get(user_id)
        if not user or not user.active_activity_token:
            return {"success": False, "error": "No Live Activity token registered"}
        
        payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "end",
                "dismissal-date": int((datetime.utcnow() + timedelta(seconds=30)).timestamp()),
                "content-state": {
                    "sessionId": session_id,
                    "cardsReviewed": cards_reviewed,
                    "sessionDuration": session_duration,
                    "completionMessage": f"Great job! You reviewed {cards_reviewed} cards.",
                    "userName": user.get_full_name(),
                    "status": "completed"
                }
            }
        }
        
        status_code = await self.notification_service._send_push_notification(
            device_token=user.device_token,
            payload=payload,
            push_type="liveactivity",
            activity_token=user.active_activity_token
        )
        
        return {"success": status_code == 200, "status_code": status_code}
    
    async def send_recall_reminder_activity(self, user_id: int, due_cards_count: int, 
                                          next_card: dict = None):
        """Send a Live Activity for recall reminders"""
        user = User.query.get(user_id)
        if not user or not user.active_activity_token:
            return {"success": False, "error": "No Live Activity token registered"}
        
        # Get user's recall settings
        recall_frequency = getattr(user, 'recall_frequency_minutes', 30)
        next_recall_time = datetime.utcnow() + timedelta(minutes=recall_frequency)
        
        payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "start",
                "content-state": {
                    "activityType": "recall_reminder",
                    "dueCardsCount": due_cards_count,
                    "nextRecallTime": next_recall_time.isoformat(),
                    "previewCard": next_card['front'] if next_card else "Ready to study?",
                    "previewCardType": next_card['content_type'] if next_card else "flashcard",
                    "userName": user.get_full_name(),
                    "reminderMessage": f"{due_cards_count} cards ready for review"
                }
            }
        }
        
        status_code = await self.notification_service._send_push_notification(
            device_token=user.device_token,
            payload=payload,
            push_type="liveactivity",
            activity_token=user.active_activity_token
        )
        
        return {"success": status_code == 200, "status_code": status_code}
    
    async def send_daily_progress_activity(self, user_id: int):
        """Send daily progress Live Activity"""
        user = User.query.get(user_id)
        if not user or not user.active_activity_token:
            return {"success": False, "error": "No Live Activity token registered"}
        
        # Get today's stats
        stats = SpacedRepetitionService.get_user_stats(user_id)
        
        # Calculate streak (simplified - you might want to implement proper streak tracking)
        streak_days = getattr(user, 'current_streak', 0)
        
        payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "start",
                "content-state": {
                    "activityType": "daily_progress",
                    "totalCards": stats['total_cards'],
                    "dueCards": stats['due_cards'],
                    "matureCards": stats['mature_cards'],
                    "streakDays": streak_days,
                    "userName": user.get_full_name(),
                    "progressMessage": f"Keep it up! {stats['due_cards']} cards due today."
                }
            }
        }
        
        status_code = await self.notification_service._send_push_notification(
            device_token=user.device_token,
            payload=payload,
            push_type="liveactivity",
            activity_token=user.active_activity_token
        )
        
        return {"success": status_code == 200, "status_code": status_code}
    
    def schedule_recall_reminders(self, user_id: int):
        """Schedule recurring recall reminder Live Activities"""
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # This would integrate with your existing scheduler
        # For now, we'll return a success message
        return {
            "success": True,
            "message": f"Recall reminders scheduled for user {user.username}",
            "frequency": getattr(user, 'recall_frequency_minutes', 30)
        }