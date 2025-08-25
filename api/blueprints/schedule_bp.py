"""
Schedule generation endpoints blueprint
"""
from flask import Blueprint, request, jsonify, current_app
from ..services.schedule_service import ScheduleService
from ..utils.response_helpers import success_response, error_response, validation_error_response
from ..utils.validators import validate_schedule_request

schedule_bp = Blueprint('schedule', __name__, url_prefix='/api')

@schedule_bp.route('/generate-schedule', methods=['POST'])
def generate_schedule():
    """Generate class schedule from calendar data"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate request data
        validation_errors = validate_schedule_request(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Extract parameters with defaults
        semester_year = data['semester_year']
        weekdays = data.get('weekdays', [])
        date_format = data.get('date_format', '')
        show_holidays = data.get('show_holidays', True)
        show_breaks = data.get('show_breaks', True)
        show_events = data.get('show_events', True)
        
        # Generate schedule
        schedule_service = ScheduleService(current_app.config['DATA_DIR'])
        schedule_result = schedule_service.generate_schedule(
            semester_year=semester_year,
            weekdays=weekdays,
            date_format=date_format,
            show_holidays=show_holidays,
            show_breaks=show_breaks,
            show_events=show_events
        )
        
        return success_response(schedule_result, 'Schedule generated successfully')
        
    except ValueError as e:
        return error_response(f'Invalid request data: {str(e)}', 400)
    except Exception as e:
        return error_response(f'Error generating schedule: {str(e)}', 500)