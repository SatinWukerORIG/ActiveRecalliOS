"""
Authentication service for user management and session handling
"""
from datetime import datetime, timedelta
from flask import request, session
from werkzeug.security import generate_password_hash
import re
from app.models import User, UserSession, PasswordResetToken
from app import db

class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None):
        """Register a new user"""
        # Validate input
        username_valid, username_msg = AuthService.validate_username(username)
        if not username_valid:
            return {'success': False, 'error': username_msg}
        
        if not AuthService.validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        
        password_valid, password_msg = AuthService.validate_password(password)
        if not password_valid:
            return {'success': False, 'error': password_msg}
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return {'success': False, 'error': 'Username already exists'}
        
        if User.query.filter_by(email=email).first():
            return {'success': False, 'error': 'Email already registered'}
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
    
    @staticmethod
    def authenticate_user(username_or_email, password):
        """Authenticate user with username/email and password"""
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        if not user.is_active:
            return {'success': False, 'error': 'Account is deactivated'}
        
        if not user.check_password(password):
            return {'success': False, 'error': 'Invalid password'}
        
        # Update last login
        user.update_last_login()
        
        return {
            'success': True,
            'user': user.to_dict(include_sensitive=True),
            'message': 'Authentication successful'
        }
    
    @staticmethod
    def login_user(username_or_email, password):
        """Login user and create session"""
        # Authenticate user
        auth_result = AuthService.authenticate_user(username_or_email, password)
        if not auth_result['success']:
            return auth_result
        
        # Create session
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        session_result = AuthService.create_session(user.id)
        if not session_result['success']:
            return session_result
        
        return {
            'success': True,
            'user': auth_result['user'],
            'session_token': session_result['session_token'],
            'message': 'Login successful'
        }
    
    @staticmethod
    def create_session(user_id, expires_in_days=30):
        """Create a new user session"""
        try:
            # Get request metadata
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            user_agent = request.environ.get('HTTP_USER_AGENT', '')
            
            # Create session
            user_session = UserSession(
                user_id=user_id,
                expires_in_days=expires_in_days,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(user_session)
            db.session.commit()
            
            return {
                'success': True,
                'session': user_session.to_dict(),
                'session_token': user_session.session_token
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Session creation failed: {str(e)}'}
    
    @staticmethod
    def validate_session(session_token):
        """Validate a session token"""
        if not session_token:
            return {'success': False, 'error': 'No session token provided'}
        
        user_session = UserSession.query.filter_by(session_token=session_token).first()
        
        if not user_session:
            return {'success': False, 'error': 'Invalid session token'}
        
        if not user_session.is_valid():
            return {'success': False, 'error': 'Session expired or inactive'}
        
        # Update last activity
        user_session.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Get user
        user = User.query.get(user_session.user_id)
        if not user or not user.is_active:
            return {'success': False, 'error': 'User account not found or inactive'}
        
        return {
            'success': True,
            'user': user.to_dict(include_sensitive=True),
            'session': user_session.to_dict()
        }
    
    @staticmethod
    def logout_user(session_token):
        """Logout user by revoking session"""
        if not session_token:
            return {'success': False, 'error': 'No session token provided'}
        
        user_session = UserSession.query.filter_by(session_token=session_token).first()
        
        if user_session:
            user_session.revoke()
            db.session.commit()
        
        return {'success': True, 'message': 'Logged out successfully'}
    
    @staticmethod
    def logout_all_sessions(user_id):
        """Logout user from all sessions"""
        UserSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        db.session.commit()
        
        return {'success': True, 'message': 'Logged out from all sessions'}
    
    @staticmethod
    def get_user_sessions(user_id):
        """Get all active sessions for a user"""
        sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
        return [session.to_dict() for session in sessions]
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.revoke()
        
        db.session.commit()
        return len(expired_sessions)
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """Update user profile information"""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        try:
            # Update allowed fields
            allowed_fields = [
                'first_name', 'last_name', 'focus_mode', 'notification_frequency', 
                'sleep_start', 'sleep_end', 'recall_enabled', 'recall_paused',
                'recall_frequency_minutes', 'recall_start_time', 'recall_end_time',
                'max_daily_recalls', 'recall_days_of_week', 'recall_folders',
                'live_activity_enabled', 'show_card_preview', 'show_progress_updates'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'user': user.to_dict(include_sensitive=True),
                'message': 'Profile updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Profile update failed: {str(e)}'}
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Verify current password
        if not user.check_password(current_password):
            return {'success': False, 'error': 'Current password is incorrect'}
        
        # Validate new password
        password_valid, password_msg = AuthService.validate_password(new_password)
        if not password_valid:
            return {'success': False, 'error': password_msg}
        
        try:
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            # Logout from all other sessions for security
            AuthService.logout_all_sessions(user_id)
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Password change failed: {str(e)}'}
    
    @staticmethod
    def create_password_reset_token(email):
        """Create password reset token"""
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if email exists for security
            return {'success': True, 'message': 'If the email exists, a reset link has been sent'}
        
        try:
            # Invalidate existing tokens
            PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({'used': True})
            
            # Create new token
            reset_token = PasswordResetToken(user_id=user.id)
            db.session.add(reset_token)
            db.session.commit()
            
            # In a real app, you would send an email here
            # For now, we'll return the token (remove in production)
            return {
                'success': True,
                'message': 'Password reset token created',
                'token': reset_token.token  # Remove this in production
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Token creation failed: {str(e)}'}
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset password using token"""
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token or not reset_token.is_valid():
            return {'success': False, 'error': 'Invalid or expired reset token'}
        
        # Validate new password
        password_valid, password_msg = AuthService.validate_password(new_password)
        if not password_valid:
            return {'success': False, 'error': password_msg}
        
        try:
            # Get user and update password
            user = User.query.get(reset_token.user_id)
            user.set_password(new_password)
            
            # Mark token as used
            reset_token.use_token()
            
            # Logout from all sessions
            AuthService.logout_all_sessions(user.id)
            
            db.session.commit()
            
            return {'success': True, 'message': 'Password reset successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Password reset failed: {str(e)}'}