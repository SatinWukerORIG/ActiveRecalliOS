"""
Web interface blueprint for Active Recall application
"""
from flask import Blueprint

web_bp = Blueprint('web', __name__)

from app.web import routes, auth_routes, notification_routes