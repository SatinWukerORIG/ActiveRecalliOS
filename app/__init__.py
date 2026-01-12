"""
Active Recall Flask Application Factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints
    from app.api import api_bp
    from app.web import web_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database initialized with current schema")
    
    return app