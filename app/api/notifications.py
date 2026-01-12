"""
Notification API endpoints
"""
from flask import request, jsonify
from app.api import api_bp
from app.models import User
from app.services.notification_service import NotificationService
from app.api.auth import require_auth
from app.services.spaced_repetition import SpacedRepetitionService
from app import db

# Initialize notification service
notification_service = NotificationService()

@api_bp.route('/users/<int:user_id>/register-device', methods=['POST'])
def register_device_token(user_id):
    """Register device token for push notifications"""
    data = request.json
    
    if not data or 'device_token' not in data:
        return jsonify({"error": "Device token is required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    success = notification_service.register_device_token(user_id, data['device_token'])
    
    if success:
        return jsonify({"message": "Device token registered successfully"})
    else:
        return jsonify({"error": "Failed to register device token"}), 500

@api_bp.route('/users/<int:user_id>/register-live-activity', methods=['POST'])
def register_live_activity_token(user_id):
    """Register Live Activity token"""
    data = request.json
    
    if not data or 'activity_token' not in data:
        return jsonify({"error": "Activity token is required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    success = notification_service.register_live_activity_token(user_id, data['activity_token'])
    
    if success:
        return jsonify({"message": "Live Activity token registered successfully"})
    else:
        return jsonify({"error": "Failed to register Live Activity token"}), 500

@api_bp.route('/users/<int:user_id>/trigger-study-mode', methods=['POST'])
def trigger_study_mode(user_id):
    """Trigger study mode notification (Live Activity)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.active_activity_token:
        return jsonify({"error": "No Live Activity token registered"}), 400
    
    # This would trigger a Live Activity update
    # For now, we'll just return success
    return jsonify({
        "message": "Study mode triggered successfully",
        "user_id": user_id
    })

@api_bp.route('/users/<int:user_id>/availability', methods=['GET'])
def check_user_availability(user_id):
    """Check if user is available for notifications"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    available = notification_service._should_send_notification(user)
    
    return jsonify({
        "available": available,
        "focus_mode": user.focus_mode,
        "has_sleep_schedule": bool(user.sleep_start and user.sleep_end)
    })

@api_bp.route('/notification-scheduler/start', methods=['POST'])
def start_notification_scheduler():
    """Start the notification scheduler"""
    notification_service.start_scheduler()
    return jsonify({"message": "Notification scheduler started"})

@api_bp.route('/notifications/test-recall', methods=['POST'])
@require_auth
def test_recall_notification():
    """Send a test recall notification"""
    user_id = request.current_user['id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get a sample due card
    due_cards = SpacedRepetitionService.get_due_cards(user_id, limit=1)
    
    if due_cards:
        card = due_cards[0]
        message = f"📚 Ready to review: {card.front[:50]}..."
    else:
        message = "🧪 Test recall notification - No cards due right now!"
    
    try:
        # Send test notification (simplified for demo)
        print(f"Would send test recall to {user.username}: {message}")
        
        return jsonify({
            "message": "Test recall notification sent!",
            "notification_content": message
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to send test notification: {str(e)}"}), 500

@api_bp.route('/notifications/status', methods=['GET'])
@require_auth
def get_notification_status():
    """Get current notification status for user"""
    user_id = request.current_user['id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Calculate status information
    due_cards_count = len(SpacedRepetitionService.get_due_cards(user_id))
    available = notification_service._should_send_notification(user) and not user.recall_paused
    
    # Calculate next recall time based on user settings
    next_recall = "Paused" if user.recall_paused else "Not scheduled"
    if user.recall_enabled and available and not user.recall_paused:
        from datetime import datetime, timedelta
        next_time = datetime.now() + timedelta(minutes=user.recall_frequency_minutes or 30)
        next_recall = next_time.strftime("%H:%M")
    
    # Get today's recall count (simplified - in production you'd track this)
    recalls_today = 0  # This would be tracked in a separate table
    
    return jsonify({
        "recalls_today": recalls_today,
        "next_recall": next_recall,
        "available": available,
        "due_cards": due_cards_count,
        "recall_enabled": user.recall_enabled,
        "recall_paused": user.recall_paused,
        "focus_mode": user.focus_mode
    }), 200

@api_bp.route('/notifications/pause', methods=['POST'])
@require_auth
def pause_notifications():
    """Pause notifications"""
    user_id = request.current_user['id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Set paused state
    user.recall_paused = True
    db.session.commit()
    
    return jsonify({
        "message": "Notifications paused",
        "paused": True
    }), 200

@api_bp.route('/notifications/resume', methods=['POST'])
@require_auth
def resume_notifications():
    """Resume notifications"""
    user_id = request.current_user['id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Resume notifications by clearing paused state
    user.recall_paused = False
    db.session.commit()
    
    return jsonify({
        "message": "Notifications resumed",
        "paused": False
    }), 200