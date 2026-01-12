"""
Authentication middleware for protecting routes
"""
from functools import wraps
from flask import session, redirect, url_for, request, g
from app.services.auth_service import AuthService

def login_required(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        
        if not session_token:
            return redirect(url_for('web.welcome'))
        
        # Validate session
        auth_result = AuthService.validate_session(session_token)
        if not auth_result['success']:
            session.clear()
            return redirect(url_for('web.welcome'))
        
        # Store user in g for template access
        g.current_user = auth_result['user']
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator to optionally load user if authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        g.current_user = None
        
        if session_token:
            auth_result = AuthService.validate_session(session_token)
            if auth_result['success']:
                g.current_user = auth_result['user']
            else:
                session.clear()
        
        return f(*args, **kwargs)
    
    return decorated_function