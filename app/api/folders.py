"""
Folder management API endpoints
"""
from flask import request, jsonify
from app.api import api_bp
from app.models import User, Folder, Card
from app.api.auth import require_auth
from app import db

@api_bp.route('/folders', methods=['GET'])
@require_auth
def get_folders():
    """Get folders for the current user with optional parent filter"""
    user_id = request.current_user['id']
    parent_id = request.args.get('parent_id', type=int)
    
    # If parent_id is provided, get subfolders; otherwise get root folders
    if parent_id is not None:
        folders = Folder.query.filter_by(user_id=user_id, parent_folder_id=parent_id).order_by(Folder.name).all()
    else:
        folders = Folder.query.filter_by(user_id=user_id, parent_folder_id=None).order_by(Folder.name).all()
    
    return jsonify({
        "folders": [folder.to_dict(include_subfolders=False) for folder in folders],
        "parent_id": parent_id
    })

@api_bp.route('/folders', methods=['POST'])
@require_auth
def create_folder():
    """Create a new folder"""
    data = request.json
    user_id = request.current_user['id']
    
    # Validate required fields
    if not data or not data.get('name'):
        return jsonify({"error": "Folder name is required"}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({"error": "Folder name cannot be empty"}), 400
    
    parent_folder_id = data.get('parent_folder_id')
    
    # Validate parent folder if provided
    if parent_folder_id:
        parent_folder = Folder.query.filter_by(id=parent_folder_id, user_id=user_id).first()
        if not parent_folder:
            return jsonify({"error": "Parent folder not found"}), 400
    
    # Check if folder name already exists at this level for this user
    existing_folder = Folder.query.filter_by(
        user_id=user_id, 
        name=name, 
        parent_folder_id=parent_folder_id
    ).first()
    if existing_folder:
        return jsonify({"error": "A folder with this name already exists at this level"}), 400
    
    # Create new folder
    folder = Folder(
        user_id=user_id,
        name=name,
        description=data.get('description', '').strip() or None,
        color=data.get('color', '#007AFF'),
        parent_folder_id=parent_folder_id
    )
    
    db.session.add(folder)
    db.session.commit()
    
    return jsonify({
        "message": "Folder created successfully",
        "folder": folder.to_dict()
    }), 201

@api_bp.route('/folders/<int:folder_id>', methods=['GET'])
@require_auth
def get_folder(folder_id):
    """Get a specific folder with its cards and subfolders"""
    user_id = request.current_user['id']
    
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "Folder not found"}), 404
    
    # Get cards in this folder (not in subfolders)
    cards = Card.query.filter_by(folder_id=folder_id, user_id=user_id).all()
    
    # Get subfolders
    subfolders = Folder.query.filter_by(parent_folder_id=folder_id, user_id=user_id).order_by(Folder.name).all()
    
    folder_data = folder.to_dict()
    folder_data['cards'] = [card.to_dict() for card in cards]
    folder_data['subfolders'] = [subfolder.to_dict() for subfolder in subfolders]
    
    return jsonify({"folder": folder_data})

@api_bp.route('/folders/all', methods=['GET'])
@require_auth
def get_all_folders():
    """Get all folders for the current user (flat list for notifications settings)"""
    user_id = request.current_user['id']
    
    folders = Folder.query.filter_by(user_id=user_id).order_by(Folder.name).all()
    
    return jsonify({
        "folders": [folder.to_dict() for folder in folders]
    })

@api_bp.route('/folders/<int:folder_id>', methods=['PUT'])
@require_auth
def update_folder(folder_id):
    """Update a folder"""
    data = request.json
    user_id = request.current_user['id']
    
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "Folder not found"}), 404
    
    # Update fields if provided
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Folder name cannot be empty"}), 400
        
        # Check if new name conflicts with existing folder
        if name != folder.name:
            existing_folder = Folder.query.filter_by(user_id=user_id, name=name).first()
            if existing_folder:
                return jsonify({"error": "A folder with this name already exists"}), 400
        
        folder.name = name
    
    if 'description' in data:
        folder.description = data['description'].strip() or None
    
    if 'color' in data:
        folder.color = data['color']
    
    db.session.commit()
    
    return jsonify({
        "message": "Folder updated successfully",
        "folder": folder.to_dict()
    })

@api_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@require_auth
def delete_folder(folder_id):
    """Delete a folder and optionally move its cards"""
    data = request.json or {}
    user_id = request.current_user['id']
    
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify({"error": "Folder not found"}), 404
    
    # Handle cards in the folder
    move_to_folder_id = data.get('move_cards_to_folder_id')
    delete_cards = data.get('delete_cards', False)
    
    cards_in_folder = Card.query.filter_by(folder_id=folder_id, user_id=user_id).all()
    
    if delete_cards:
        # Delete all cards in the folder
        for card in cards_in_folder:
            db.session.delete(card)
    elif move_to_folder_id:
        # Move cards to another folder
        target_folder = Folder.query.filter_by(id=move_to_folder_id, user_id=user_id).first()
        if not target_folder:
            return jsonify({"error": "Target folder not found"}), 404
        
        for card in cards_in_folder:
            card.folder_id = move_to_folder_id
    else:
        # Move cards to no folder (root level)
        for card in cards_in_folder:
            card.folder_id = None
    
    # Delete the folder
    db.session.delete(folder)
    db.session.commit()
    
    return jsonify({
        "message": "Folder deleted successfully",
        "cards_affected": len(cards_in_folder)
    })

@api_bp.route('/cards/<int:card_id>/move', methods=['PUT'])
@require_auth
def move_card_to_folder(card_id):
    """Move a card to a different folder"""
    data = request.json
    user_id = request.current_user['id']
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({"error": "Card not found"}), 404
    
    folder_id = data.get('folder_id')
    
    if folder_id is not None:
        # Validate folder exists and belongs to user
        if folder_id != 0:  # 0 means move to root (no folder)
            folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
            if not folder:
                return jsonify({"error": "Folder not found"}), 404
            card.folder_id = folder_id
        else:
            card.folder_id = None
    
    db.session.commit()
    
    return jsonify({
        "message": "Card moved successfully",
        "card": card.to_dict()
    })