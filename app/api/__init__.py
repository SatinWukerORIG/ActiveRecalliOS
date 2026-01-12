"""
API Blueprint for Active Recall application
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import cards, users, content_generation, notifications, import_export, auth, live_activity, folders