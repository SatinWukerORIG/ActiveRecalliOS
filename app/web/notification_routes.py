"""
Notification settings web routes
"""
from flask import render_template, redirect, url_for, session
from app.web import web_bp
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import login_required

@web_bp.route('/notifications')
@login_required
def notification_settings():
    """Notification settings page"""
    # Check authentication
    session_token = session.get('session_token')
    if not session_token:
        return redirect(url_for('web.login'))
    
    auth_result = AuthService.validate_session(session_token)
    if not auth_result['success']:
        session.clear()
        return redirect(url_for('web.login'))
    
    return render_template('notifications/settings.html', user=auth_result['user'])

@web_bp.route('/notifications/setup')
@login_required
def notification_setup():
    """Initial notification setup page"""
    session_token = session.get('session_token')
    if not session_token:
        return redirect(url_for('web.login'))
    
    auth_result = AuthService.validate_session(session_token)
    if not auth_result['success']:
        session.clear()
        return redirect(url_for('web.login'))
    
    return render_template('notifications/setup.html', user=auth_result['user'])