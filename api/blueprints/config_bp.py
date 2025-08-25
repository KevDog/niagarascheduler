"""
Configuration endpoints blueprint
"""
from flask import Blueprint, jsonify, current_app
from ..services.schedule_service import ScheduleService
from ..utils.response_helpers import success_response, error_response

config_bp = Blueprint('config', __name__, url_prefix='/api')

@config_bp.route('/config', methods=['GET'])
def get_config():
    """Get application configuration data"""
    try:
        schedule_service = ScheduleService(current_app.config['DATA_DIR'])
        
        # Get available semesters
        available_semesters = schedule_service.get_available_semesters()
        
        # Get date formats
        date_formats = schedule_service.get_date_formats()
        
        # Static configuration
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        days = [str(d) for d in range(1, 32)]
        
        config_data = {
            'semesters': available_semesters,
            'months': months,
            'days': days,
            'date_formats': date_formats,
            'api_version': current_app.config['API_VERSION'],
            'api_title': current_app.config['API_TITLE']
        }
        
        return success_response(config_data)
        
    except Exception as e:
        return error_response(f'Error loading configuration: {str(e)}', 500)