"""
Enhanced Live Activity API endpoints for unlock-triggered content updates
"""
from flask import request, jsonify
from app.api import api_bp
from app.api.auth import require_auth
from app.services.live_activity_enhanced import live_activity_service
import asyncio

@api_bp.route('/live-activity/start', methods=['POST'])
@require_auth
def start_live_activity():
    """Start a Live Activity with initial study content"""
    user_id = request.current_user['id']
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(live_activity_service.start_live_activity(user_id))
        loop.close()
        
        if result['success']:
            return jsonify({
                "message": "Live Activity started successfully",
                "card_id": result.get('card_id'),
                "content_type": result.get('content_type')
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to start Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/unlock-update', methods=['POST'])
@require_auth
def update_on_unlock():
    """Update Live Activity content when phone is unlocked"""
    user_id = request.current_user['id']
    device_info = request.json or {}
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.handle_unlock_webhook(user_id, device_info)
        )
        loop.close()
        
        if result['success']:
            return jsonify({
                "message": "Live Activity updated with new content",
                "card_id": result.get('card_id'),
                "content_type": result.get('content_type'),
                "content": result.get('content')
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/end', methods=['POST'])
@require_auth
def end_live_activity():
    """End the Live Activity"""
    user_id = request.current_user['id']
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(live_activity_service.end_live_activity(user_id))
        loop.close()
        
        if result['success']:
            return jsonify({"message": "Live Activity ended successfully"}), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to end Live Activity: {str(e)}"}), 500

@api_bp.route('/live-activity/status', methods=['GET'])
@require_auth
def get_live_activity_status():
    """Get current Live Activity status"""
    user_id = request.current_user['id']
    
    try:
        status = live_activity_service.get_user_live_activity_status(user_id)
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

# Webhook endpoint for iOS app to call when phone is unlocked
@api_bp.route('/webhook/phone-unlock', methods=['POST'])
def phone_unlock_webhook():
    """Webhook endpoint for iOS to call when phone is unlocked"""
    data = request.json or {}
    
    # Validate required fields
    user_id = data.get('user_id')
    device_token = data.get('device_token')  # For basic authentication
    
    if not user_id or not device_token:
        return jsonify({"error": "Missing user_id or device_token"}), 400
    
    # Basic validation - check if device token matches user
    from app.models import User
    user = User.query.get(user_id)
    if not user or user.device_token != device_token:
        return jsonify({"error": "Invalid user or device token"}), 401
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.handle_unlock_webhook(user_id, data)
        )
        loop.close()
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({"error": f"Webhook processing failed: {str(e)}"}), 500

@api_bp.route('/live-activity/test-content', methods=['POST'])
@require_auth
def test_live_activity_content():
    """Test endpoint to manually trigger Live Activity content update"""
    user_id = request.current_user['id']
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            live_activity_service.update_live_activity_on_unlock(user_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify({
                "message": "Test Live Activity update sent",
                "card_id": result.get('card_id'),
                "content_type": result.get('content_type'),
                "content": result.get('content')
            }), 200
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Test failed: {str(e)}"}), 500