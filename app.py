import os
import json
import time
import jwt
import httpx
from datetime import datetime, timedelta, time as dt_time
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import threading
import schedule
import openai
import re
from typing import List, Dict, Any

# --- CONFIGURATION ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///active_recall.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# APNs Settings (You will fill these from your Apple Developer Account)
APNS_AUTH_KEY_ID = os.environ.get("APNS_AUTH_KEY_ID", "")
APNS_TEAM_ID = os.environ.get("APNS_TEAM_ID", "")
BUNDLE_ID = "com.yourname.recallapp" # Your app's bundle ID
APNS_KEY_PATH = "AuthKey_XXXXXXXXXX.p8" # Path to your .p8 file
ALGORITHM = "ES256"

# OpenAI Settings for LLM Integration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# --- DATABASE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # Token for Path A (Standard/Rich Push)
    device_token = db.Column(db.String(255)) 
    # Token for Path B (Temporary Live Activity Token)
    active_activity_token = db.Column(db.String(255))
    
    # User preferences
    focus_mode = db.Column(db.Boolean, default=False)
    sleep_start = db.Column(db.Time, nullable=True)  # Sleep schedule
    sleep_end = db.Column(db.Time, nullable=True)
    notification_frequency = db.Column(db.Integer, default=30)  # minutes
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    cards = db.relationship('Card', backref='user', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Content Type: 'flashcard' or 'information'
    content_type = db.Column(db.String(20), default='flashcard', nullable=False)
    
    # For flashcards: front = question, back = answer
    # For information: front = content, back = null/empty
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=True)
    
    # Subject/Category organization
    subject = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    
    # Spaced Repetition (SM-2) Variables
    interval = db.Column(db.Integer, default=0)    # Current gap in days
    ease_factor = db.Column(db.Float, default=2.5) # Difficulty multiplier
    repetition_count = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ai_generated = db.Column(db.Boolean, default=False)

class ContentGeneration(db.Model):
    """Track AI content generation requests and results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Input data
    source_material = db.Column(db.Text, nullable=False)  # Original text/material
    generation_type = db.Column(db.String(20), nullable=False)  # 'flashcards', 'information', 'mixed'
    subject = db.Column(db.String(100), nullable=True)
    
    # Generation settings
    max_cards = db.Column(db.Integer, default=10)
    difficulty_level = db.Column(db.String(20), default='medium')  # 'easy', 'medium', 'hard'
    
    # Results
    cards_generated = db.Column(db.Integer, default=0)
    generation_status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    error_message = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='content_generations')

# --- DATABASE MIGRATION ---

def migrate_database():
    """Handle database schema migrations"""
    print("Database initialized with current schema")

# --- CORE LOGIC: SPACED REPETITION (SM-2) ---

def sm2_update(quality, interval, ease_factor, repetition):
    """
    quality: 0-5 (0: Blackout, 3: Difficult, 5: Perfect)
    Returns: (new_interval, new_ease_factor, new_repetition)
    """
    if quality >= 3:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetition += 1
    else:
        repetition = 0
        interval = 1

    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3
        
    return interval, ease_factor, repetition

# --- SMART SCHEDULING SYSTEM ---

def is_user_available(user):
    """Check if user is available for notifications based on context"""
    now = datetime.utcnow()
    current_time = now.time()
    
    # Check focus mode
    if user.focus_mode:
        return False
    
    # Check sleep schedule
    if user.sleep_start and user.sleep_end:
        sleep_start = user.sleep_start
        sleep_end = user.sleep_end
        
        # Handle sleep schedule that crosses midnight
        if sleep_start > sleep_end:
            # Sleep schedule crosses midnight (e.g., 23:00 to 07:00)
            if current_time >= sleep_start or current_time <= sleep_end:
                return False
        else:
            # Normal sleep schedule (e.g., 22:00 to 06:00)
            if sleep_start <= current_time <= sleep_end:
                return False
    
    return True

def get_next_due_card(user_id):
    """Get the next card due for review for a user"""
    now = datetime.utcnow()
    card = Card.query.filter(
        Card.user_id == user_id,
        Card.next_review <= now
    ).order_by(Card.next_review).first()
    
    return card

async def send_study_notification(user, card):
    """Send a smart study notification to the user"""
    if not user.device_token:
        print(f"No device token for user {user.id}")
        return False
    
    # Create notification payload
    if card.content_type == "flashcard":
        payload = {
            "aps": {
                "alert": {
                    "title": "Active Recall",
                    "body": card.front,
                    "subtitle": f"Subject: {card.subject or 'General'}"
                },
                "sound": "default",
                "category": "FLASHCARD_CATEGORY",
                "mutable-content": 1
            },
            "card_id": card.id,
            "content_type": card.content_type
        }
    else:
        payload = {
            "aps": {
                "alert": {
                    "title": "Active Recall",
                    "body": card.front,
                    "subtitle": f"Subject: {card.subject or 'General'}"
                },
                "sound": "default",
                "category": "INFORMATION_CATEGORY",
                "mutable-content": 1
            },
            "card_id": card.id,
            "content_type": card.content_type
        }
    
    try:
        status = await send_push_notification(user.device_token, payload, push_type="alert")
        print(f"Sent notification to user {user.id}, card {card.id}, status: {status}")
        return status == 200
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False

def schedule_user_notifications():
    """Check all users and send notifications for due cards"""
    print("Checking for users with due cards...")
    
    users = User.query.all()
    for user in users:
        if not is_user_available(user):
            continue
        
        card = get_next_due_card(user.id)
        if card:
            # Run async function in thread
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(send_study_notification(user, card))
                loop.close()
                
                if success:
                    print(f"Sent notification to user {user.username} for card: {card.front[:50]}...")
            except Exception as e:
                print(f"Error sending notification to user {user.id}: {e}")

def start_notification_scheduler():
    """Start the background notification scheduler"""
    # Schedule notifications every 5 minutes (for testing)
    # In production, this could be more frequent or use a more sophisticated system
    schedule.every(5).minutes.do(schedule_user_notifications)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Notification scheduler started")

# --- LLM CONTENT GENERATION SYSTEM ---

class ContentGenerator:
    """AI-powered content generation using OpenAI GPT"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    def generate_flashcards(self, source_material: str, subject: str = None, max_cards: int = 10, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate flashcards from source material"""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = self._build_flashcard_prompt(source_material, subject, max_cards, difficulty)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in concised spaced repetition flashcards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_flashcards(content)
            
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            raise
    
    def generate_information_pieces(self, source_material: str, subject: str = None, max_pieces: int = 10, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate information pieces (facts, formulas, concepts) from source material"""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = self._build_information_prompt(source_material, subject, max_pieces, difficulty)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting key information and creating concise memorable learning content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_information_pieces(content)
            
        except Exception as e:
            print(f"Error generating information pieces: {e}")
            raise
    
    def generate_mixed_content(self, source_material: str, subject: str = None, max_items: int = 10, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate a mix of flashcards and information pieces"""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        # Split between flashcards and information pieces
        flashcard_count = max_items // 2
        info_count = max_items - flashcard_count
        
        flashcards = self.generate_flashcards(source_material, subject, flashcard_count, difficulty)
        info_pieces = self.generate_information_pieces(source_material, subject, info_count, difficulty)
        
        return flashcards + info_pieces
    
    def _build_flashcard_prompt(self, source_material: str, subject: str, max_cards: int, difficulty: str) -> str:
        """Build prompt for flashcard generation"""
        difficulty_guidance = {
            "easy": "Focus on basic concepts and definitions. Use simple language.",
            "medium": "Include both basic and intermediate concepts. Balance detail with clarity.",
            "hard": "Include complex concepts and detailed explanations. Challenge advanced learners."
        }
        
        prompt = f"""
Create {max_cards} high-quality flashcards from the following material.

Subject: {subject or 'General'}
Difficulty: {difficulty} - {difficulty_guidance.get(difficulty, '')}

Source Material:
{source_material}

Requirements:
1. Create exactly {max_cards} flashcards
2. Each flashcard should have a clear, concise question and a complete answer
3. Focus on the most important concepts and facts
4. Questions should test understanding, not just memorization
5. Vary question types (what, how, why, when, where)
6. Keep questions under 100 characters when possible
7. Answers should be comprehensive but concise

Format your response as:
Q1: [Question]
A1: [Answer]

Q2: [Question]
A2: [Answer]

...and so on.
"""
        return prompt
    
    def _build_information_prompt(self, source_material: str, subject: str, max_pieces: int, difficulty: str) -> str:
        """Build prompt for information piece generation"""
        prompt = f"""
Extract {max_pieces} key information pieces from the following material that would be valuable for spaced repetition learning.

Subject: {subject or 'General'}
Difficulty: {difficulty}

Source Material:
{source_material}

Requirements:
1. Extract exactly {max_pieces} key facts, formulas, concepts, or important statements
2. Each piece should be self-contained and memorable
3. Focus on information that benefits from repetition (formulas, definitions, key facts)
4. Keep each piece concise but complete
5. Include formulas, dates, names, definitions, and key concepts
6. Prioritize information that students commonly forget

Format your response as:
INFO1: [Key information piece]
INFO2: [Key information piece]
...and so on.
"""
        return prompt
    
    def _parse_flashcards(self, content: str) -> List[Dict[str, Any]]:
        """Parse generated flashcards from LLM response"""
        flashcards = []
        lines = content.strip().split('\n')
        
        current_question = None
        current_answer = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match question pattern (Q1:, Q2:, etc.)
            q_match = re.match(r'^Q\d+:\s*(.+)$', line)
            if q_match:
                current_question = q_match.group(1).strip()
                continue
            
            # Match answer pattern (A1:, A2:, etc.)
            a_match = re.match(r'^A\d+:\s*(.+)$', line)
            if a_match and current_question:
                current_answer = a_match.group(1).strip()
                
                flashcards.append({
                    'content_type': 'flashcard',
                    'front': current_question,
                    'back': current_answer
                })
                
                current_question = None
                current_answer = None
        
        return flashcards
    
    def _parse_information_pieces(self, content: str) -> List[Dict[str, Any]]:
        """Parse generated information pieces from LLM response"""
        info_pieces = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match info pattern (INFO1:, INFO2:, etc.)
            info_match = re.match(r'^INFO\d+:\s*(.+)$', line)
            if info_match:
                info_content = info_match.group(1).strip()
                
                info_pieces.append({
                    'content_type': 'information',
                    'front': info_content,
                    'back': None
                })
        
        return info_pieces

# Initialize content generator
content_generator = ContentGenerator()

# --- APNS INTEGRATION (PATH A & B) ---

def create_apns_token():
    """Generates the JWT required to authenticate with Apple."""
    with open(APNS_KEY_PATH, "r") as f:
        secret = f.read()

    token = jwt.encode(
        {
            "iss": APNS_TEAM_ID,
            "iat": time.time(),
        },
        secret,
        algorithm=ALGORITHM,
        headers={"alg": ALGORITHM, "kid": APNS_AUTH_KEY_ID},
    )
    return token

async def send_push_notification(device_token, payload, push_type="alert", activity_token=None):
    """
    Sends notification to APNs.
    push_type can be 'alert' (Path A) or 'liveactivity' (Path B)
    """
    token = create_apns_token()
    url = f"https://api.development.push.apple.com/3/device/{device_token if not activity_token else activity_token}"
    
    headers = {
        "apns-topic": BUNDLE_ID if push_type == "alert" else f"{BUNDLE_ID}.push-type.liveactivity",
        "authorization": f"bearer {token}",
        "apns-push-type": push_type,
        "apns-priority": "10"
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.status_code

# --- API ENDPOINTS ---

# Web Interface
@app.route('/')
def index():
    """Serve the web interface for content management"""
    return render_template('index.html')

# User Management
@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400
    
    new_user = User(
        username=data['username'],
        email=data.get('email'),
        notification_frequency=data.get('notification_frequency', 30)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created", "user_id": new_user.id}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "focus_mode": user.focus_mode,
        "notification_frequency": user.notification_frequency,
        "created_at": user.created_at.isoformat()
    })

@app.route('/users/<int:user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    """Update user preferences (focus mode, sleep schedule, etc.)"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if 'focus_mode' in data:
        user.focus_mode = data['focus_mode']
    if 'notification_frequency' in data:
        user.notification_frequency = data['notification_frequency']
    if 'sleep_start' in data and data['sleep_start']:
        user.sleep_start = datetime.strptime(data['sleep_start'], '%H:%M').time()
    if 'sleep_end' in data and data['sleep_end']:
        user.sleep_end = datetime.strptime(data['sleep_end'], '%H:%M').time()
    
    user.last_active = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Preferences updated"})

# Content Management
@app.route('/cards', methods=['POST'])
def add_card():
    """Add a new flashcard or information piece"""
    data = request.json
    
    new_card = Card(
        user_id=data['user_id'],
        content_type=data.get('content_type', 'flashcard'),
        front=data['front'],
        back=data.get('back', ''),  # Optional for information pieces
        subject=data.get('subject'),
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None,
        is_ai_generated=data.get('is_ai_generated', False)
    )
    db.session.add(new_card)
    db.session.commit()
    return jsonify({"message": "Card added", "card_id": new_card.id}), 201

@app.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get a specific card"""
    card = Card.query.get_or_404(card_id)
    return jsonify({
        "id": card.id,
        "content_type": card.content_type,
        "front": card.front,
        "back": card.back,
        "subject": card.subject,
        "tags": json.loads(card.tags) if card.tags else [],
        "next_review": card.next_review.isoformat(),
        "is_ai_generated": card.is_ai_generated
    })

@app.route('/users/<int:user_id>/cards', methods=['GET'])
def get_user_cards(user_id):
    """Get all cards for a user with optional filtering"""
    subject = request.args.get('subject')
    content_type = request.args.get('content_type')
    
    query = Card.query.filter_by(user_id=user_id)
    
    if subject:
        query = query.filter_by(subject=subject)
    if content_type:
        query = query.filter_by(content_type=content_type)
    
    cards = query.all()
    
    return jsonify({
        "cards": [{
            "id": card.id,
            "content_type": card.content_type,
            "front": card.front,
            "back": card.back,
            "subject": card.subject,
            "tags": json.loads(card.tags) if card.tags else [],
            "next_review": card.next_review.isoformat(),
            "is_ai_generated": card.is_ai_generated
        } for card in cards]
    })

@app.route('/users/<int:user_id>/cards/due', methods=['GET'])
def get_due_cards(user_id):
    """Get cards due for review"""
    now = datetime.utcnow()
    cards = Card.query.filter(
        Card.user_id == user_id,
        Card.next_review <= now
    ).order_by(Card.next_review).all()
    
    return jsonify({
        "due_cards": [{
            "id": card.id,
            "content_type": card.content_type,
            "front": card.front,
            "back": card.back,
            "subject": card.subject
        } for card in cards]
    })

@app.route('/users/<int:user_id>/subjects', methods=['GET'])
def get_user_subjects(user_id):
    """Get all subjects for a user"""
    subjects = db.session.query(Card.subject).filter(
        Card.user_id == user_id,
        Card.subject.isnot(None)
    ).distinct().all()
    
    return jsonify({
        "subjects": [subject[0] for subject in subjects if subject[0]]
    })

@app.route('/review/<int:card_id>', methods=['POST'])
def review_card(card_id):
    """Handle the user's response to a question (e.g. from a Rich Notification)"""
    data = request.json
    quality = data.get('quality', 3) # 0 to 5

    card = Card.query.get_or_404(card_id)

    interval, ease, rep = sm2_update(quality, card.interval, card.ease_factor, card.repetition_count)

    card.interval = interval
    card.ease_factor = ease
    card.repetition_count = rep
    card.next_review = datetime.utcnow() + timedelta(days=interval)

    # Update user's last active time
    user = User.query.get(card.user_id)
    user.last_active = datetime.utcnow()

    db.session.commit()
    return jsonify({
        "message": "SRS Updated", 
        "next_review": card.next_review.isoformat(),
        "interval": interval,
        "ease_factor": ease
    })

# Utility endpoints
@app.route('/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user learning statistics"""
    total_cards = Card.query.filter_by(user_id=user_id).count()
    due_cards = Card.query.filter(
        Card.user_id == user_id,
        Card.next_review <= datetime.utcnow()
    ).count()
    
    # Cards by subject
    subjects_stats = db.session.query(
        Card.subject, 
        db.func.count(Card.id)
    ).filter_by(user_id=user_id).group_by(Card.subject).all()
    
    return jsonify({
        "total_cards": total_cards,
        "due_cards": due_cards,
        "subjects": {subject: count for subject, count in subjects_stats if subject}
    })

@app.route('/register-device', methods=['POST'])
def register_device():
    """Register device token for standard push notifications"""
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user.device_token = data['device_token']
    db.session.commit()
    return jsonify({"message": "Device token registered"}), 200
@app.route('/register-live-activity', methods=['POST'])
def register_activity():
    """Path B: Store the special token generated by iOS for the Live Activity widget."""
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user.active_activity_token = data['activity_token']
    db.session.commit()
    return jsonify({"message": "Live Activity Token Registered"}), 200

@app.route('/trigger-study-mode/<int:user_id>', methods=['POST'])
async def trigger_study_mode(user_id):
    """
    Path B Demo: Sends a push that updates the Live Activity widget 
    with a new question without a standard alert.
    """
    user = User.query.get(user_id)
    if not user or not user.active_activity_token:
        return jsonify({"error": "No active activity"}), 400

    # Get a card due for review
    card = Card.query.filter(Card.user_id == user_id).order_by(Card.next_review).first()

    payload = {
        "aps": {
            "timestamp": int(time.time()),
            "event": "update",
            "content-state": {
                "question": card.front,
                "progress": 0.5 # Example progress metadata
            }
        }
    }

    status = await send_push_notification(None, payload, push_type="liveactivity", activity_token=user.active_activity_token)
    return jsonify({"apns_status": status})

# Smart Notification Endpoints
@app.route('/send-study-notification/<int:user_id>', methods=['POST'])
async def send_study_notification_endpoint(user_id):
    """Manually trigger a study notification for a user"""
    user = User.query.get_or_404(user_id)
    
    if not is_user_available(user):
        return jsonify({"error": "User is not available (focus mode or sleep time)"}), 400
    
    card = get_next_due_card(user_id)
    if not card:
        return jsonify({"message": "No cards due for review"}), 200
    
    success = await send_study_notification(user, card)
    
    if success:
        return jsonify({
            "message": "Notification sent successfully",
            "card_id": card.id,
            "card_front": card.front
        })
    else:
        return jsonify({"error": "Failed to send notification"}), 500

@app.route('/users/<int:user_id>/availability', methods=['GET'])
def check_user_availability(user_id):
    """Check if a user is currently available for notifications"""
    user = User.query.get_or_404(user_id)
    available = is_user_available(user)
    
    reasons = []
    if user.focus_mode:
        reasons.append("Focus mode is enabled")
    
    if user.sleep_start and user.sleep_end:
        now = datetime.utcnow().time()
        sleep_start = user.sleep_start
        sleep_end = user.sleep_end
        
        # Check if currently in sleep time
        if sleep_start > sleep_end:
            if now >= sleep_start or now <= sleep_end:
                reasons.append("Currently in sleep schedule")
        else:
            if sleep_start <= now <= sleep_end:
                reasons.append("Currently in sleep schedule")
    
    return jsonify({
        "available": available,
        "reasons": reasons if not available else [],
        "next_due_card": get_next_due_card(user_id).id if get_next_due_card(user_id) else None
    })

@app.route('/users/<int:user_id>/schedule-notifications', methods=['POST'])
def schedule_notifications_for_user(user_id):
    """Enable/disable automatic notifications for a user"""
    data = request.json
    user = User.query.get_or_404(user_id)
    
    # This could be extended to store per-user scheduling preferences
    # For now, we'll just return the current status
    
    return jsonify({
        "message": "Notification scheduling updated",
        "user_id": user_id,
        "notification_frequency": user.notification_frequency
    })

# LLM Content Generation Endpoints
@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Generate flashcards and/or information pieces from source material using AI"""
    data = request.json
    
    # Validate required fields
    required_fields = ['user_id', 'source_material', 'generation_type']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    user_id = data['user_id']
    source_material = data['source_material']
    generation_type = data['generation_type']  # 'flashcards', 'information', 'mixed'
    
    # Optional parameters
    subject = data.get('subject')
    max_cards = data.get('max_cards', 10)
    difficulty_level = data.get('difficulty_level', 'medium')
    
    # Validate user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if OpenAI is configured
    if not OPENAI_API_KEY:
        return jsonify({"error": "AI content generation not configured. Please set OPENAI_API_KEY environment variable."}), 503
    
    # Create generation record
    generation = ContentGeneration(
        user_id=user_id,
        source_material=source_material,
        generation_type=generation_type,
        subject=subject,
        max_cards=max_cards,
        difficulty_level=difficulty_level
    )
    db.session.add(generation)
    db.session.commit()
    
    try:
        # Generate content based on type
        if generation_type == 'flashcards':
            generated_items = content_generator.generate_flashcards(
                source_material, subject, max_cards, difficulty_level
            )
        elif generation_type == 'information':
            generated_items = content_generator.generate_information_pieces(
                source_material, subject, max_cards, difficulty_level
            )
        elif generation_type == 'mixed':
            generated_items = content_generator.generate_mixed_content(
                source_material, subject, max_cards, difficulty_level
            )
        else:
            return jsonify({"error": "Invalid generation_type. Must be 'flashcards', 'information', or 'mixed'"}), 400
        
        # Save generated cards to database
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
        # Update generation record with error
        generation.generation_status = 'failed'
        generation.error_message = str(e)
        generation.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "error": "Failed to generate content",
            "details": str(e),
            "generation_id": generation.id
        }), 500

@app.route('/users/<int:user_id>/generations', methods=['GET'])
def get_user_generations(user_id):
    """Get content generation history for a user"""
    user = User.query.get_or_404(user_id)
    
    generations = ContentGeneration.query.filter_by(user_id=user_id).order_by(
        ContentGeneration.created_at.desc()
    ).all()
    
    return jsonify({
        "generations": [{
            "id": gen.id,
            "generation_type": gen.generation_type,
            "subject": gen.subject,
            "cards_generated": gen.cards_generated,
            "generation_status": gen.generation_status,
            "difficulty_level": gen.difficulty_level,
            "created_at": gen.created_at.isoformat(),
            "completed_at": gen.completed_at.isoformat() if gen.completed_at else None,
            "error_message": gen.error_message
        } for gen in generations]
    })

@app.route('/generations/<int:generation_id>', methods=['GET'])
def get_generation_details(generation_id):
    """Get detailed information about a specific content generation"""
    generation = ContentGeneration.query.get_or_404(generation_id)
    
    # Get cards created from this generation
    cards = Card.query.filter_by(
        user_id=generation.user_id,
        is_ai_generated=True
    ).filter(
        Card.created_at >= generation.created_at
    ).all()
    
    return jsonify({
        "generation": {
            "id": generation.id,
            "user_id": generation.user_id,
            "source_material": generation.source_material,
            "generation_type": generation.generation_type,
            "subject": generation.subject,
            "max_cards": generation.max_cards,
            "difficulty_level": generation.difficulty_level,
            "cards_generated": generation.cards_generated,
            "generation_status": generation.generation_status,
            "error_message": generation.error_message,
            "created_at": generation.created_at.isoformat(),
            "completed_at": generation.completed_at.isoformat() if generation.completed_at else None
        },
        "generated_cards": [{
            "id": card.id,
            "content_type": card.content_type,
            "front": card.front,
            "back": card.back,
            "subject": card.subject
        } for card in cards]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate_database()
        
        # Start the notification scheduler
        start_notification_scheduler()
        
    # Use the new run.py instead of this legacy file
    print("⚠️  This is the legacy app.py file.")
    print("🔄 Please use 'python3 run.py' instead for the new modular version with port management.")
    print("🚀 Starting legacy version with port management...")
    
    from app.utils.port_manager import PortManager
    
    try:
        port = PortManager.get_port_from_env_or_find(
            env_var='PORT',
            preferred_ports=[5001, 5002, 8000, 8001, 4000]
        )
        PortManager.print_port_info(port)
        app.run(debug=True, port=port, host='0.0.0.0')
    except Exception as e:
        print(f"❌ Error with port management: {e}")
        print("💡 Falling back to manual port selection...")
        print("🔧 Try: export PORT=8000 && python3 app.py")
        import sys
        sys.exit(1)
