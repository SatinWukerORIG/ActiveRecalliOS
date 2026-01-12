"""
Card API endpoints
"""
from flask import request, jsonify
from datetime import datetime
from app.api import api_bp
from app.models import User, Card, Folder
from app.services.spaced_repetition import SpacedRepetitionService
from app import db

@api_bp.route('/cards', methods=['POST'])
def create_card():
    """Create a new card (flashcard or information piece)"""
    data = request.json
    
    # Validate required fields
    required_fields = ['user_id', 'content_type', 'front']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate content type
    if data['content_type'] not in ['flashcard', 'information']:
        return jsonify({"error": "content_type must be 'flashcard' or 'information'"}), 400
    
    # Validate user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # For flashcards, back field is required
    if data['content_type'] == 'flashcard' and not data.get('back'):
        return jsonify({"error": "Back field is required for flashcards"}), 400
    
    # Validate folder if provided
    folder_id = data.get('folder_id')
    if folder_id is not None:
        folder = Folder.query.filter_by(id=folder_id, user_id=data['user_id']).first()
        if not folder:
            return jsonify({"error": "Folder not found or does not belong to user"}), 404
    
    # Create card
    card = Card(
        user_id=data['user_id'],
        folder_id=data.get('folder_id'),  # Add folder_id support
        content_type=data['content_type'],
        front=data['front'],
        back=data.get('back'),
        subject=data.get('subject'),
        tags=','.join(data.get('tags', [])) if data.get('tags') else None
    )
    
    db.session.add(card)
    db.session.commit()
    
    return jsonify({
        "message": "Card created successfully",
        "card": card.to_dict()
    }), 201

@api_bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get a specific card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    return jsonify({"card": card.to_dict()})

@api_bp.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    """Update a card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    data = request.json
    
    # Update allowed fields
    if 'front' in data:
        card.front = data['front']
    if 'back' in data:
        card.back = data['back']
    if 'subject' in data:
        card.subject = data['subject']
    if 'tags' in data:
        card.tags = ','.join(data['tags']) if data['tags'] else None
    if 'folder_id' in data:
        # Validate folder if provided
        folder_id = data['folder_id']
        if folder_id is not None:
            folder = Folder.query.filter_by(id=folder_id, user_id=card.user_id).first()
            if not folder:
                return jsonify({"error": "Folder not found or does not belong to user"}), 404
        card.folder_id = folder_id
    
    db.session.commit()
    
    return jsonify({
        "message": "Card updated successfully",
        "card": card.to_dict()
    })

@api_bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    db.session.delete(card)
    db.session.commit()
    
    return jsonify({"message": "Card deleted successfully"})

@api_bp.route('/cards/<int:card_id>/review', methods=['POST'])
def review_card(card_id):
    """Review a card and update spaced repetition"""
    data = request.json
    
    if 'quality' not in data:
        return jsonify({"error": "Quality rating is required"}), 400
    
    quality = data['quality']
    if not isinstance(quality, int) or quality < 0 or quality > 5:
        return jsonify({"error": "Quality must be an integer between 0 and 5"}), 400
    
    card = SpacedRepetitionService.review_card(card_id, quality)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    return jsonify({
        "message": "Card reviewed successfully",
        "card": card.to_dict()
    })

@api_bp.route('/users/<int:user_id>/review-session', methods=['GET'])
def get_review_session(user_id):
    """Get cards for a review session"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    batch_size = request.args.get('batch_size', 5, type=int)
    cards = SpacedRepetitionService.get_next_review_batch(user_id, batch_size)
    
    return jsonify({
        "cards": [card.to_dict() for card in cards],
        "session_size": len(cards)
    })

@api_bp.route('/users/<int:user_id>/due-cards', methods=['GET'])
def get_due_cards(user_id):
    """Get cards due for review"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    limit = request.args.get('limit', type=int)
    cards = SpacedRepetitionService.get_due_cards(user_id, limit)
    
    return jsonify({
        "cards": [card.to_dict() for card in cards],
        "count": len(cards)
    })