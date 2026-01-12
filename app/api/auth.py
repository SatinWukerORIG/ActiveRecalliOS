"""
Authentication API endpoints
"""
from flask import request, jsonify, session
from functools import wraps
from app.api import api_bp
from app.services.auth_service import AuthService
from app.models import User

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get session token from header or session
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            session_token = session_token[7:]  # Remove 'Bearer ' prefix
        else:
            session_token = session.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        auth_result = AuthService.validate_session(session_token)
        if not auth_result['success']:
            return jsonify({'error': auth_result['error']}), 401
        
        # Add user to request context
        request.current_user = auth_result['user']
        request.current_session = auth_result['session']
        
        return f(*args, **kwargs)
    
    return decorated_function

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Optional fields
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    
    # Register user
    result = AuthService.register_user(
        username=data['username'].strip(),
        email=data['email'].strip().lower(),
        password=data['password'],
        first_name=first_name if first_name else None,
        last_name=last_name if last_name else None
    )
    
    if result['success']:
        return jsonify({
            'message': result['message'],
            'user': result['user']
        }), 201
    else:
        return jsonify({'error': result['error']}), 400

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Authenticate user
    auth_result = AuthService.authenticate_user(
        username_or_email=data['username'].strip(),
        password=data['password']
    )
    
    if not auth_result['success']:
        return jsonify({'error': auth_result['error']}), 401
    
    # Create session
    session_result = AuthService.create_session(
        user_id=auth_result['user']['id'],
        expires_in_days=data.get('remember_me', False) and 30 or 7
    )
    
    if not session_result['success']:
        return jsonify({'error': session_result['error']}), 500
    
    # Store session token in Flask session for web interface
    session['session_token'] = session_result['session_token']
    session['user_id'] = auth_result['user']['id']
    
    return jsonify({
        'message': 'Login successful',
        'user': auth_result['user'],
        'session_token': session_result['session_token'],
        'expires_at': session_result['session']['expires_at']
    }), 200

@api_bp.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    session_token = request.headers.get('Authorization')
    if session_token and session_token.startswith('Bearer '):
        session_token = session_token[7:]
    else:
        session_token = session.get('session_token')
    
    # Logout user
    result = AuthService.logout_user(session_token)
    
    # Clear Flask session
    session.clear()
    
    return jsonify({'message': result['message']}), 200

@api_bp.route('/auth/logout-all', methods=['POST'])
@require_auth
def logout_all():
    """Logout user from all sessions"""
    user_id = request.current_user['id']
    
    result = AuthService.logout_all_sessions(user_id)
    
    # Clear Flask session
    session.clear()
    
    return jsonify({'message': result['message']}), 200

@api_bp.route('/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    return jsonify({
        'user': request.current_user,
        'session': request.current_session
    }), 200

@api_bp.route('/auth/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_id = request.current_user['id']
    
    result = AuthService.update_user_profile(user_id, **data)
    
    if result['success']:
        return jsonify({
            'message': result['message'],
            'user': result['user']
        }), 200
    else:
        return jsonify({'error': result['error']}), 400

@api_bp.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['current_password', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    user_id = request.current_user['id']
    
    result = AuthService.change_password(
        user_id=user_id,
        current_password=data['current_password'],
        new_password=data['new_password']
    )
    
    if result['success']:
        # Clear session since all sessions are logged out
        session.clear()
        return jsonify({'message': result['message']}), 200
    else:
        return jsonify({'error': result['error']}), 400

@api_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    result = AuthService.create_password_reset_token(data['email'].strip().lower())
    
    # Always return success for security (don't reveal if email exists)
    return jsonify({'message': result['message']}), 200

@api_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['token', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    result = AuthService.reset_password(
        token=data['token'],
        new_password=data['new_password']
    )
    
    if result['success']:
        return jsonify({'message': result['message']}), 200
    else:
        return jsonify({'error': result['error']}), 400

@api_bp.route('/auth/sessions', methods=['GET'])
@require_auth
def get_user_sessions():
    """Get user's active sessions"""
    user_id = request.current_user['id']
    sessions = AuthService.get_user_sessions(user_id)
    
    return jsonify({'sessions': sessions}), 200

@api_bp.route('/auth/validate', methods=['GET'])
def validate_session():
    """Validate session token"""
    session_token = request.headers.get('Authorization')
    if session_token and session_token.startswith('Bearer '):
        session_token = session_token[7:]
    else:
        session_token = session.get('session_token')
    
    if not session_token:
        return jsonify({'valid': False, 'error': 'No session token'}), 401
    
    result = AuthService.validate_session(session_token)
    
    if result['success']:
        return jsonify({
            'valid': True,
            'user': result['user']
        }), 200
    else:
        return jsonify({
            'valid': False,
            'error': result['error']
        }), 401