"""
Configuration settings for Active Recall application
"""
import os
from .utils.port_manager import PortManager

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = None  # Will be set dynamically
    
    # APNs Settings
    APNS_AUTH_KEY_ID = os.environ.get("APNS_AUTH_KEY_ID", "")
    APNS_TEAM_ID = os.environ.get("APNS_TEAM_ID", "")
    BUNDLE_ID = os.environ.get("BUNDLE_ID", "com.yourname.recallapp")
    APNS_KEY_PATH = os.environ.get("APNS_KEY_PATH", "AuthKey_XXXXXXXXXX.p8")
    ALGORITHM = "ES256"
    
    # OpenAI Settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    
    # Notification Settings
    DEFAULT_NOTIFICATION_FREQUENCY = 30  # minutes
    MAX_DAILY_NOTIFICATIONS = 50
    
    @staticmethod
    def get_port():
        """Get an available port using the PortManager"""
        if Config.PORT is None:
            # Preferred ports for Active Recall (avoiding 5000)
            preferred_ports = [5001, 5002, 8000, 8001, 4000]
            Config.PORT = PortManager.get_port_from_env_or_find(
                env_var='PORT',
                preferred_ports=preferred_ports
            )
        return Config.PORT
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///active_recall_dev.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///active_recall.db'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}