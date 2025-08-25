"""
Courses endpoints blueprint
"""
from flask import Blueprint, jsonify, current_app
from ..services.course_service import CourseService
from ..utils.response_helpers import success_response, error_response

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course information"""
    try:
        course_service = CourseService(
            current_app.data_loader,
            current_app.config['DATA_DIR']
        )
        
        course = course_service.get_course_by_id(course_id.upper())
        
        if not course:
            return error_response('Course not found', 404)
        
        return success_response(course)
        
    except Exception as e:
        return error_response(f'Error loading course: {str(e)}', 500)