"""
Flask application factory for Niagara University Scheduler API
"""
import os
from flask import Flask
from flask_cors import CORS
from .config import get_config
from .blueprints import (
    config_bp, departments_bp, courses_bp, offerings_bp,
    schedule_bp, syllabus_bp, health_bp
)
from core.data_loader import DepartmentDataLoader

def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app
    
    Args:
        config_name: Configuration environment name ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize CORS with configuration
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Initialize data loader and attach to app
    try:
        app.data_loader = DepartmentDataLoader(app.config['DATA_DIR'])
        app.logger.info(f"Data loader initialized with directory: {app.config['DATA_DIR']}")
    except Exception as e:
        app.logger.error(f"Failed to initialize data loader: {str(e)}")
        raise
    
    # Register blueprints
    app.register_blueprint(config_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(offerings_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(syllabus_bp)
    app.register_blueprint(health_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log registered routes in development
    if app.config['DEBUG']:
        with app.app_context():
            app.logger.info("Registered routes:")
            for rule in app.url_map.iter_rules():
                app.logger.info(f"  {rule.methods} {rule.rule}")
    
    app.logger.info(f"Application created with config: {config_class.__name__}")
    return app

def register_error_handlers(app):
    """
    Register global error handlers
    
    Args:
        app: Flask application instance
    """
    from .utils.response_helpers import error_response
    
    @app.errorhandler(404)
    def not_found_error(error):
        return error_response('Endpoint not found', 404)
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return error_response('Method not allowed', 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {str(error)}')
        return error_response('Internal server error', 500)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        return error_response('An unexpected error occurred', 500)