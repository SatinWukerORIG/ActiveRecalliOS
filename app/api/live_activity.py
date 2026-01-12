"""
Live Activity API endpoints for iOS
"""
from flask import request, jsonify
from datetime import datetime
import asyncio
from app.api import api_bp
from app.api.auth import require_auth
from app.services.live_activity_service import LiveActivityService
from app.services.spaced_repetition import SpacedRepetitionService
from app.models import User, Card

# Initialize Live Activity service
live_activity_service = LiveActivityService()

@api_bp.route('/live-activity/start-session', methods=['POST'])
@require_auth
def start_study_session_activity():
    """Start a Live Activity for a study session"""
    user_id = request.current_user['id']
    
    # Get study session cards
    cards = SpacedRepetitionService.get_next_review_batch(user_id, 10)
    session_cards = [card.to_dict() for card in cards]
    
    if not session_cards:
        return jsonify({"error": "No cards available for study session"}), 400
    
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.start_study_session_activity(user_id, session_cards)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to start Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/update-progress', methods=['POST'])
@require_auth
def update_study_progress():
    """Update Live Activity with study progress"""
    data = request.json
    user_id = request.current_user['id']
    
    required_fields = ['session_id', 'current_card_index', 'cards_reviewed', 'total_cards']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Get current card info if provided
        current_card = None
        if 'current_card_id' in data:
            card = Card.query.get(data['current_card_id'])
            if card and card.user_id == user_id:
                current_card = card.to_dict()
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.update_study_progress(
                user_id=user_id,
                session_id=data['session_id'],
                current_card_index=data['current_card_index'],
                cards_reviewed=data['cards_reviewed'],
                total_cards=data['total_cards'],
                current_card=current_card
            )
        )
        loop.close()
        
        if result['success']:
            return jsonify({"message": "Live Activity updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update Live Activity"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/end-session', methods=['POST'])
@require_auth
def end_study_session_activity():
    """End a Live Activity study session"""
    data = request.json
    user_id = request.current_user['id']
    
    required_fields = ['session_id', 'cards_reviewed', 'session_duration']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.end_study_session_activity(
                user_id=user_id,
                session_id=data['session_id'],
                cards_reviewed=data['cards_reviewed'],
                session_duration=data['session_duration']
            )
        )
        loop.close()
        
        if result['success']:
            return jsonify({"message": "Study session Live Activity ended successfully"}), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to end Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/recall-reminder', methods=['POST'])
@require_auth
def send_recall_reminder_activity():
    """Send a recall reminder Live Activity"""
    user_id = request.current_user['id']
    
    # Get due cards
    due_cards = SpacedRepetitionService.get_due_cards(user_id, limit=1)
    due_cards_count = len(SpacedRepetitionService.get_due_cards(user_id))
    
    next_card = due_cards[0].to_dict() if due_cards else None
    
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.send_recall_reminder_activity(
                user_id=user_id,
                due_cards_count=due_cards_count,
                next_card=next_card
            )
        )
        loop.close()
        
        if result['success']:
            return jsonify({
                "message": "Recall reminder Live Activity sent successfully",
                "due_cards_count": due_cards_count
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to send recall reminder: {str(e)}"}), 500

@api_bp.route('/live-activity/daily-progress', methods=['POST'])
@require_auth
def send_daily_progress_activity():
    """Send daily progress Live Activity"""
    user_id = request.current_user['id']
    
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.send_daily_progress_activity(user_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify({"message": "Daily progress Live Activity sent successfully"}), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to send daily progress: {str(e)}"}), 500

@api_bp.route('/live-activity/test', methods=['POST'])
@require_auth
def test_live_activity():
    """Send a test Live Activity"""
    user_id = request.current_user['id']
    user = User.query.get(user_id)
    
    if not user or not user.active_activity_token:
        return jsonify({"error": "No Live Activity token registered. Please register from the iOS app first."}), 400
    
    try:
        # Create a test Live Activity
        test_payload = {
            "aps": {
                "timestamp": int(datetime.utcnow().timestamp()),
                "event": "start",
                "content-state": {
                    "activityType": "test",
                    "testMessage": "🧪 Test Live Activity",
                    "userName": user.get_full_name(),
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                    "status": "This is a test Live Activity from Active Recall!"
                }
            }
        }
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status_code = loop.run_until_complete(
            live_activity_service.notification_service._send_push_notification(
                device_token=user.device_token,
                payload=test_payload,
                push_type="liveactivity",
                activity_token=user.active_activity_token
            )
        )
        loop.close()
        
        if status_code == 200:
            return jsonify({
                "message": "Test Live Activity sent successfully! Check your iPhone home screen.",
                "status_code": status_code
            }), 200
        else:
            return jsonify({
                "error": f"Failed to send test Live Activity (status: {status_code})",
                "status_code": status_code
            }), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to send test Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/schedule-reminders', methods=['POST'])
@require_auth
def schedule_recall_reminders():
    """Schedule recurring recall reminder Live Activities"""
    user_id = request.current_user['id']
    
    try:
        result = live_activity_service.schedule_recall_reminders(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to schedule reminders: {str(e)}"}), 500