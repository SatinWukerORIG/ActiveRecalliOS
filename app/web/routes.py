"""
Web interface routes
"""
from flask import render_template, request, jsonify, redirect, url_for, session, g
from app.web import web_bp
from app.models import User, Card, Folder
from app.services.spaced_repetition import SpacedRepetitionService
from app.services.ai_content_generator import AIContentGenerator
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import login_required, optional_auth
from app import db

# Initialize services
ai_generator = AIContentGenerator()

@web_bp.route('/')
@login_required
def index():
    """Main web interface - requires authentication"""
    return render_template('index.html', user=g.current_user)

@web_bp.route('/welcome')
def welcome():
    """Welcome page - no authentication required"""
    # Check if user is already logged in
    session_token = session.get('session_token')
    if session_token:
        auth_result = AuthService.validate_session(session_token)
        if auth_result['success']:
            return redirect(url_for('web.index'))
        else:
            # Clear invalid session
            session.clear()
    
    return render_template('welcome.html')

@web_bp.route('/study')
@login_required
def study_interface():
    """Study session interface - requires authentication"""
    return render_template('study.html', user=g.current_user)

@web_bp.route('/analytics')
@login_required
def analytics():
    """Analytics and progress tracking - requires authentication"""
    return render_template('analytics.html', user=g.current_user)

# Legacy API endpoints for web interface compatibility (now with auth)
@web_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """Create user (web interface compatibility) - deprecated, use registration"""
    return jsonify({"error": "Use /register endpoint for user creation"}), 400

@web_bp.route('/users/<int:user_id>')
@login_required
def get_user(user_id):
    """Get user (web interface compatibility)"""
    # Only allow users to access their own data
    if g.current_user['id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": user.to_dict()})

@web_bp.route('/users/<int:user_id>/stats')
@login_required
def get_user_stats(user_id):
    """Get user stats (web interface compatibility)"""
    # Only allow users to access their own data
    if g.current_user['id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    stats = SpacedRepetitionService.get_user_stats(user_id)
    return jsonify(stats)

@web_bp.route('/users/<int:user_id>/cards')
@login_required
def get_user_cards(user_id):
    """Get user cards (web interface compatibility)"""
    # Only allow users to access their own data
    if g.current_user['id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    cards = [card.to_dict() for card in user.cards]
    return jsonify({"cards": cards})

@web_bp.route('/cards', methods=['POST'])
@login_required
def create_card():
    """Create card (web interface compatibility)"""
    data = request.json
    
    # Override user_id with current user's ID for security
    data['user_id'] = g.current_user['id']
    
    required_fields = ['content_type', 'front']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if data['content_type'] not in ['flashcard', 'information']:
        return jsonify({"error": "content_type must be 'flashcard' or 'information'"}), 400
    
    if data['content_type'] == 'flashcard' and not data.get('back'):
        return jsonify({"error": "Back field is required for flashcards"}), 400
    
    # Validate folder if provided
    folder_id = data.get('folder_id')
    if folder_id is not None:
        folder = Folder.query.filter_by(id=folder_id, user_id=data['user_id']).first()
        if not folder:
            return jsonify({"error": "Folder not found or does not belong to user"}), 404
    
    card = Card(
        user_id=data['user_id'],
        folder_id=folder_id,  # Add folder_id support
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

@web_bp.route('/generate-content', methods=['POST'])
@login_required
def generate_content():
    """Generate content (web interface compatibility)"""
    # Handle both form data (with files) and JSON data
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle file uploads
        source_material = request.form.get('source_material', '').strip()
        generation_type = request.form.get('generation_type', 'mixed')
        subject = request.form.get('subject', '').strip() or None
        max_cards = int(request.form.get('max_cards', 10))
        focus_areas = request.form.get('focus_areas', '').strip()
        
        # Parse focus areas
        focus_areas_list = []
        if focus_areas:
            focus_areas_list = [area.strip() for area in focus_areas.split(',') if area.strip()]
        
        # Process uploaded files
        pdf_content = None
        images = []
        
        # Handle PDF upload
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            if pdf_file and pdf_file.filename and pdf_file.filename.lower().endswith('.pdf'):
                pdf_content = pdf_file.read()
        
        # Handle image uploads
        if 'images' in request.files:
            image_files = request.files.getlist('images')
            for image_file in image_files[:5]:  # Limit to 5 images
                if image_file and image_file.filename:
                    image_content = image_file.read()
                    images.append(image_content)
    else:
        # Handle JSON data (legacy compatibility)
        data = request.json or {}
        source_material = data.get('source_material', '').strip()
        generation_type = data.get('generation_type', 'mixed')
        subject = data.get('subject', '').strip() or None
        max_cards = data.get('max_cards', 10)
        focus_areas_list = []
        pdf_content = None
        images = []
    
    user_id = g.current_user['id']
    
    # Validate that at least one input is provided
    if not source_material and not pdf_content and not images:
        return jsonify({"error": "Source material, PDF, or images are required"}), 400
    
    if not ai_generator.is_available():
        return jsonify({
            "error": "AI content generation not configured. Please set OPENAI_API_KEY environment variable."
        }), 503
    
    try:
        if generation_type == 'flashcards':
            generated_items = ai_generator.generate_flashcards(
                source_material, subject, max_cards, focus_areas_list, images, pdf_content
            )
        elif generation_type == 'information':
            generated_items = ai_generator.generate_information_pieces(
                source_material, subject, max_cards, focus_areas_list, images, pdf_content
            )
        elif generation_type == 'mixed':
            generated_items = ai_generator.generate_mixed_content(
                source_material, subject, max_cards, focus_areas_list, images, pdf_content
            )
        else:
            return jsonify({"error": "Invalid generation_type"}), 400
        
        created_cards = []
        for item in generated_items:
            card = Card(
                user_id=user_id,
                content_type=item['content_type'],
                front=item['front'],
                back=item.get('back'),
                subject=subject,
                is_ai_generated=True
            )
            db.session.add(card)
            created_cards.append({
                'content_type': item['content_type'],
                'front': item['front'],
                'back': item.get('back')
            })
        
        db.session.commit()
        
        return jsonify({
            "message": "Content generated successfully",
            "generation_id": "web-generated",
            "cards_generated": len(created_cards),
            "cards": created_cards
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": "Failed to generate content",
            "details": str(e)
        }), 500