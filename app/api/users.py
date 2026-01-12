"""
User API endpoints
"""
from flask import request, jsonify
from app.api import api_bp
from app.models import User
from app.services.spaced_repetition import SpacedRepetitionService
from app import db

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    if not data or 'username' not in data:
        return jsonify({"error": "Username is required"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409
    
    user = User(
        username=data['username'],
        email=data.get('email')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict()
    }), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": user.to_dict()})

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user preferences"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    
    # Update allowed fields
    if 'focus_mode' in data:
        user.focus_mode = data['focus_mode']
    if 'notification_frequency' in data:
        user.notification_frequency = data['notification_frequency']
    if 'sleep_start' in data:
        user.sleep_start = data['sleep_start']
    if 'sleep_end' in data:
        user.sleep_end = data['sleep_end']
    
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    })

@api_bp.route('/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user learning statistics"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    stats = SpacedRepetitionService.get_user_stats(user_id)
    return jsonify(stats)

@api_bp.route('/users/<int:user_id>/cards', methods=['GET'])
def get_user_cards(user_id):
    """Get all cards for a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    cards = [card.to_dict() for card in user.cards]
    return jsonify({"cards": cards})