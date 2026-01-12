"""
Database models for Active Recall application
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import secrets
from app import db

class User(UserMixin, db.Model):
    """Enhanced User model with authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Push notification tokens
    device_token = db.Column(db.String(255))  # Standard push notifications
    active_activity_token = db.Column(db.String(255))  # Live Activity token
    
    # User preferences
    focus_mode = db.Column(db.Boolean, default=False)
    sleep_start = db.Column(db.Time, nullable=True)
    sleep_end = db.Column(db.Time, nullable=True)
    notification_frequency = db.Column(db.Integer, default=30)  # minutes
    
    # Recall notification settings
    recall_enabled = db.Column(db.Boolean, default=True)
    recall_paused = db.Column(db.Boolean, default=False)  # Simple pause/resume state
    recall_frequency_minutes = db.Column(db.Integer, default=30)  # How often to send recalls
    recall_start_time = db.Column(db.Time, nullable=True)  # When to start sending recalls
    recall_end_time = db.Column(db.Time, nullable=True)    # When to stop sending recalls
    max_daily_recalls = db.Column(db.Integer, default=20)  # Maximum recalls per day
    recall_days_of_week = db.Column(db.String(20), default='1,2,3,4,5,6,7')  # Days of week (1=Monday)
    recall_folders = db.Column(db.Text, nullable=True)  # Comma-separated folder IDs for recall (null = all folders)
    
    # Live Activity preferences
    live_activity_enabled = db.Column(db.Boolean, default=True)
    show_card_preview = db.Column(db.Boolean, default=True)
    show_progress_updates = db.Column(db.Boolean, default=True)
    
    # Notification tracking
    last_notification_time = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    cards = db.relationship('Card', backref='user', lazy=True, cascade='all, delete-orphan')
    content_generations = db.relationship('ContentGeneration', backref='user', lazy=True)
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'focus_mode': self.focus_mode,
            'notification_frequency': self.notification_frequency,
            'recall_enabled': self.recall_enabled,
            'recall_paused': self.recall_paused,
            'recall_frequency_minutes': self.recall_frequency_minutes,
            'recall_start_time': self.recall_start_time.strftime('%H:%M') if self.recall_start_time else None,
            'recall_end_time': self.recall_end_time.strftime('%H:%M') if self.recall_end_time else None,
            'max_daily_recalls': self.max_daily_recalls,
            'recall_days_of_week': self.recall_days_of_week,
            'recall_folders': self.recall_folders,
            'live_activity_enabled': self.live_activity_enabled,
            'show_card_preview': self.show_card_preview,
            'show_progress_updates': self.show_progress_updates,
            'sleep_start': self.sleep_start.strftime('%H:%M') if self.sleep_start else None,
            'sleep_end': self.sleep_end.strftime('%H:%M') if self.sleep_end else None
        }
        return data

class UserSession(db.Model):
    """User session management"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Session metadata
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, expires_in_days=30, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.session_token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if session is valid"""
        return self.is_active and not self.is_expired()
    
    def extend_session(self, days=30):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(days=days)
        self.last_activity = datetime.utcnow()
    
    def revoke(self):
        """Revoke session"""
        self.is_active = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_token': self.session_token,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

class PasswordResetToken(db.Model):
    """Password reset tokens"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, user_id, expires_in_hours=24, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid"""
        return not self.used and not self.is_expired()
    
    def use_token(self):
        """Mark token as used"""
        self.used = True

class Folder(db.Model):
    """Folder model for organizing cards with hierarchical support"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)  # For nested folders
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#007AFF')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='folder', lazy=True)
    user = db.relationship('User', backref='folders')
    
    # Self-referential relationship for nested folders
    subfolders = db.relationship('Folder', backref=db.backref('parent_folder', remote_side=[id]), lazy=True)
    
    def get_all_cards_count(self):
        """Get count of cards in this folder and all subfolders"""
        count = len(self.cards)
        for subfolder in self.subfolders:
            count += subfolder.get_all_cards_count()
        return count
    
    def get_path(self):
        """Get the full path to this folder"""
        if self.parent_folder:
            return self.parent_folder.get_path() + [self.name]
        return [self.name]
    
    def to_dict(self, include_subfolders=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'parent_folder_id': self.parent_folder_id,
            'created_at': self.created_at.isoformat(),
            'card_count': len(self.cards),
            'total_card_count': self.get_all_cards_count(),
            'path': self.get_path()
        }
        
        if include_subfolders:
            data['subfolders'] = [subfolder.to_dict() for subfolder in self.subfolders]
        
        return data

class Card(db.Model):
    """Card model supporting both flashcards and information pieces"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)  # Optional folder organization
    
    # Content
    content_type = db.Column(db.String(20), nullable=False)  # 'flashcard' or 'information'
    front = db.Column(db.Text, nullable=False)  # Question or information content
    back = db.Column(db.Text, nullable=True)   # Answer (only for flashcards)
    subject = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    
    # Spaced Repetition (SM-2 Algorithm)
    interval = db.Column(db.Integer, default=1)  # Days until next review
    ease_factor = db.Column(db.Float, default=2.5)  # Difficulty multiplier
    repetition_count = db.Column(db.Integer, default=0)  # Number of successful reviews
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, nullable=True)
    is_ai_generated = db.Column(db.Boolean, default=False)
    
    def update_spaced_repetition(self, quality):
        """Update spaced repetition variables based on SM-2 algorithm"""
        if quality >= 3:  # Correct response
            if self.repetition_count == 0:
                self.interval = 1
            elif self.repetition_count == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
            
            self.repetition_count += 1
        else:  # Incorrect response
            self.repetition_count = 0
            self.interval = 1
        
        # Update ease factor
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Set next review date
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        self.last_reviewed = datetime.utcnow()
    
    def is_due_for_review(self):
        """Check if card is due for review"""
        return datetime.utcnow() >= self.next_review
    
    def to_dict(self):
        return {
            'id': self.id,
            'content_type': self.content_type,
            'front': self.front,
            'back': self.back,
            'subject': self.subject,
            'tags': self.tags.split(',') if self.tags else [],
            'folder_id': self.folder_id,
            'folder_name': self.folder.name if self.folder else None,
            'interval': self.interval,
            'ease_factor': self.ease_factor,
            'repetition_count': self.repetition_count,
            'next_review': self.next_review.isoformat(),
            'created_at': self.created_at.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'is_ai_generated': self.is_ai_generated,
            'is_due': self.is_due_for_review()
        }

class ContentGeneration(db.Model):
    """Track AI content generation requests and results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Generation parameters
    source_material = db.Column(db.Text, nullable=False)
    generation_type = db.Column(db.String(20), nullable=False)  # 'flashcards', 'information', 'mixed'
    subject = db.Column(db.String(100), nullable=True)
    max_cards = db.Column(db.Integer, default=10)
    focus_areas = db.Column(db.Text, nullable=True)  # Comma-separated focus areas
    
    # Results
    cards_generated = db.Column(db.Integer, default=0)
    generation_status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'generation_type': self.generation_type,
            'subject': self.subject,
            'max_cards': self.max_cards,
            'focus_areas': self.focus_areas,
            'cards_generated': self.cards_generated,
            'generation_status': self.generation_status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }