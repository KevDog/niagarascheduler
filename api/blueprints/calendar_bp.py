"""
Calendar Blueprint for Academic Calendar API

This blueprint provides endpoints for accessing academic calendar data,
generating class meeting dates, and retrieving semester events.
"""

from flask import Blueprint, request, current_app
from api.services.calendar_service import CalendarService
from api.utils.response_helpers import success_response, error_response
import logging

logger = logging.getLogger(__name__)
calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')

def get_calendar_service() -> CalendarService:
    """Get or create calendar service instance"""
    if not hasattr(current_app, 'calendar_service'):
        current_app.calendar_service = CalendarService()
    return current_app.calendar_service

@calendar_bp.route('/<semester>', methods=['GET'])
def get_calendar(semester: str):
    """Get complete calendar data for a semester"""
    try:
        calendar_service = get_calendar_service()
        calendar_data = calendar_service.get_calendar(semester)
        
        if not calendar_data:
            return error_response(
                f"Calendar data not found for semester: {semester}",
                status_code=404
            )
        
        return success_response({
            'calendar': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar for {semester}: {str(e)}")
        return error_response("Failed to retrieve calendar data")

@calendar_bp.route('/<semester>/events', methods=['GET'])
def get_semester_events(semester: str):
    """Get academic events for a semester"""
    try:
        calendar_service = get_calendar_service()
        
        # Get optional event type filters
        event_types = request.args.getlist('types')
        
        events = calendar_service.get_semester_events(semester, event_types or None)
        
        return success_response({
            'semester': semester,
            'events': events,
            'total_events': len(events)
        })
        
    except Exception as e:
        logger.error(f"Error getting events for {semester}: {str(e)}")
        return error_response("Failed to retrieve semester events")

@calendar_bp.route('/<semester>/class-dates', methods=['POST'])
def generate_class_dates(semester: str):
    """Generate specific class meeting dates based on schedule"""
    try:
        calendar_service = get_calendar_service()
        data = request.get_json() or {}
        
        # Required parameters
        meeting_days = data.get('meeting_days', '')
        if not meeting_days:
            return error_response("meeting_days parameter is required")
        
        # Optional parameters
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        class_dates = calendar_service.generate_class_dates(
            semester=semester,
            meeting_days=meeting_days,
            start_date=start_date,
            end_date=end_date
        )
        
        # Also get relevant events
        events = calendar_service.get_semester_events(
            semester, 
            ['holiday', 'academic_deadline', 'semester_event']
        )
        
        return success_response({
            'semester': semester,
            'meeting_days': meeting_days,
            'class_dates': class_dates,
            'total_classes': len(class_dates),
            'academic_events': events
        })
        
    except Exception as e:
        logger.error(f"Error generating class dates for {semester}: {str(e)}")
        return error_response("Failed to generate class dates")

@calendar_bp.route('/available-semesters', methods=['GET'])
def get_available_semesters():
    """Get list of available semester calendars"""
    try:
        # This could be made dynamic by scanning the calendars directory
        available_semesters = [
            {
                'key': '25_FA',
                'display': 'Fall 2025',
                'semester': 'fall_2025'
            },
            {
                'key': '26_SP', 
                'display': 'Spring 2026',
                'semester': 'spring_2026'
            }
        ]
        
        return success_response({
            'semesters': available_semesters
        })
        
    except Exception as e:
        logger.error(f"Error getting available semesters: {str(e)}")
        return error_response("Failed to retrieve available semesters")