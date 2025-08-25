"""
Configuration management for Niagara University Scheduler API
"""
import os

class Config:
    """Base configuration"""
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # API Configuration
    API_VERSION = '1.0.0'
    API_TITLE = 'Niagara University Scheduler API'
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production CORS origins should be configured via environment
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(config_name=None):
    """Get configuration class by name"""
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    return config_map.get(config_name, DevelopmentConfig)