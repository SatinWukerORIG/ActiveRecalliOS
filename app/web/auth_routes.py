"""
Authentication web routes
"""
from flask import render_template, redirect, url_for, session, request
from app.web import web_bp
from app.services.auth_service import AuthService

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and form processing"""
    if request.method == 'POST':
        # Process login form
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('auth/login.html', error='Username and password are required')
        
        # Attempt login
        result = AuthService.login_user(username, password)
        
        if result['success']:
            # Set session
            session['session_token'] = result['session_token']
            return redirect(url_for('web.index'))
        else:
            return render_template('auth/login.html', error=result['error'])
    
    # GET request - show login form
    # Check if user is already logged in
    session_token = session.get('session_token')
    if session_token:
        auth_result = AuthService.validate_session(session_token)
        if auth_result['success']:
            return redirect(url_for('web.index'))
        else:
            # Clear invalid session
            session.clear()
    
    return render_template('auth/login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and form processing"""
    if request.method == 'POST':
        # Process registration form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not username or not email or not password:
            return render_template('auth/register.html', error='Username, email, and password are required')
        
        # Attempt registration
        result = AuthService.register_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if result['success']:
            # Auto-login after registration
            login_result = AuthService.login_user(username, password)
            if login_result['success']:
                session['session_token'] = login_result['session_token']
                return redirect(url_for('web.index'))
            else:
                return redirect(url_for('web.login'))
        else:
            return render_template('auth/register.html', error=result['error'])
    
    # GET request - show registration form
    # Check if user is already logged in
    session_token = session.get('session_token')
    if session_token:
        auth_result = AuthService.validate_session(session_token)
        if auth_result['success']:
            return redirect(url_for('web.index'))
        else:
            # Clear invalid session
            session.clear()
    
    return render_template('auth/register.html')

@web_bp.route('/logout')
def logout():
    """Logout and redirect to login"""
    session_token = session.get('session_token')
    if session_token:
        AuthService.logout_user(session_token)
    
    session.clear()
    return redirect(url_for('web.login'))

@web_bp.route('/profile')
def profile():
    """User profile page"""
    # Check authentication
    session_token = session.get('session_token')
    if not session_token:
        return redirect(url_for('web.login'))
    
    auth_result = AuthService.validate_session(session_token)
    if not auth_result['success']:
        session.clear()
        return redirect(url_for('web.login'))
    
    return render_template('auth/profile.html', user=auth_result['user'])

@web_bp.route('/reset-password')
def reset_password():
    """Password reset page"""
    token = request.args.get('token')
    if not token:
        return redirect(url_for('web.login'))
    
    return render_template('auth/reset_password.html', token=token)