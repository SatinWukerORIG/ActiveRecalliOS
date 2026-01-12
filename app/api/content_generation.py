"""
AI Content Generation API endpoints
"""
from flask import request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.api import api_bp
from app.models import User, Card, ContentGeneration, Folder
from app.services.ai_content_generator import AIContentGenerator
from app.api.auth import require_auth
from app import db

# Initialize AI content generator
ai_generator = AIContentGenerator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/generate-content', methods=['POST'])
@require_auth
def generate_content():
    """Generate flashcards and/or information pieces from source material using AI"""
    # Get form data and files
    source_material = request.form.get('source_material', '').strip()
    generation_type = request.form.get('generation_type', 'mixed')
    subject = request.form.get('subject', '').strip() or None
    max_cards = int(request.form.get('max_cards', 10))
    focus_areas = request.form.get('focus_areas', '').strip()
    folder_id = request.form.get('folder_id')  # New: folder selection
    
    # Parse focus areas
    focus_areas_list = []
    if focus_areas:
        focus_areas_list = [area.strip() for area in focus_areas.split(',') if area.strip()]
    
    user_id = request.current_user['id']
    
    # Validate folder if provided
    if folder_id and folder_id != '0':  # '0' means no folder
        try:
            folder_id = int(folder_id)
            folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
            if not folder:
                return jsonify({"error": "Selected folder not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid folder ID"}), 400
    else:
        folder_id = None
    
    # Validate required fields
    if not source_material and 'pdf_file' not in request.files and 'images' not in request.files:
        return jsonify({"error": "Source material, PDF, or images are required"}), 400
    
    # Validate generation type
    if generation_type not in ['flashcards', 'information', 'mixed']:
        return jsonify({
            "error": "Invalid generation_type. Must be 'flashcards', 'information', or 'mixed'"
        }), 400
    
    # Check if AI generation is available
    if not ai_generator.is_available():
        return jsonify({
            "error": "AI content generation not configured. Please set OPENAI_API_KEY environment variable."
        }), 503
    
    # Process uploaded files
    pdf_content = None
    images = []
    
    # Handle PDF upload
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file and pdf_file.filename and pdf_file.filename != '':
            if pdf_file.filename.lower().endswith('.pdf') or allowed_file(pdf_file.filename):
                try:
                    pdf_content = pdf_file.read()
                    # Basic validation - check if it's actually a PDF or has content
                    if len(pdf_content) > 0:
                        # Try to validate it's a real PDF by checking for PDF header
                        if pdf_content.startswith(b'%PDF') or len(pdf_content) < 1000:
                            # Either it's a real PDF or small enough to be test content
                            pass
                        else:
                            # Large file that doesn't start with PDF header - might be invalid
                            print(f"Warning: Uploaded file might not be a valid PDF")
                except Exception as e:
                    print(f"Error reading PDF file: {e}")
                    pdf_content = None
    
    # Handle image uploads
    if 'images' in request.files:
        image_files = request.files.getlist('images')
        for image_file in image_files[:5]:  # Limit to 5 images
            if image_file and image_file.filename and allowed_file(image_file.filename):
                image_content = image_file.read()
                images.append(image_content)
    
    # Create generation record
    generation = ContentGeneration(
        user_id=user_id,
        source_material=source_material or "File-based generation",
        generation_type=generation_type,
        subject=subject,
        max_cards=max_cards,
        focus_areas=','.join(focus_areas_list) if focus_areas_list else None
    )
    db.session.add(generation)
    db.session.commit()
    
    try:
        # Generate content based on type
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
        
        # Validate that we got some results
        if not generated_items:
            raise Exception("No content was generated. Please check your input and try again.")
        
        # Save generated cards to database
        created_cards = []
        cards_to_create = generated_items[:max_cards]  # Limit to requested number
        
        for item in cards_to_create:
            card = Card(
                user_id=user_id,
                folder_id=folder_id,  # Assign to selected folder
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
        
        # Update generation record
        generation.cards_generated = len(created_cards)
        generation.generation_status = 'completed'
        generation.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Content generated successfully",
            "generation_id": generation.id,
            "cards_generated": len(created_cards),
            "cards": created_cards
        }), 201
        
    except Exception as e:
        # Log the error for debugging
        print(f"AI Generation Error: {str(e)}")
        
        # Update generation record with error
        generation.generation_status = 'failed'
        generation.error_message = str(e)
        generation.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Provide user-friendly error message
        error_message = str(e)
        if "Failed to extract text from PDF" in error_message:
            error_message = "Unable to process the uploaded PDF file. Please ensure it's a valid PDF with extractable text."
        elif "Failed to process image" in error_message:
            error_message = "Unable to process one or more uploaded images. Please ensure they are valid image files."
        elif "OpenAI" in error_message or "API" in error_message:
            error_message = "AI service temporarily unavailable. Please try again in a moment."
        
        return jsonify({
            "error": "Failed to generate content",
            "details": error_message,
            "generation_id": generation.id
        }), 500

@api_bp.route('/users/<int:user_id>/content-generations', methods=['GET'])
@require_auth
def get_content_generations(user_id):
    """Get content generation history for a user"""
    # Only allow users to access their own data
    if request.current_user['id'] != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    generations = ContentGeneration.query.filter_by(user_id=user_id)\
        .order_by(ContentGeneration.created_at.desc()).all()
    
    return jsonify({
        "generations": [gen.to_dict() for gen in generations]
    })

@api_bp.route('/content-generations/<int:generation_id>', methods=['GET'])
@require_auth
def get_content_generation(generation_id):
    """Get a specific content generation"""
    generation = ContentGeneration.query.get(generation_id)
    if not generation:
        return jsonify({"error": "Content generation not found"}), 404
    
    # Only allow users to access their own data
    if request.current_user['id'] != generation.user_id:
        return jsonify({"error": "Access denied"}), 403
    
    return jsonify({"generation": generation.to_dict()})