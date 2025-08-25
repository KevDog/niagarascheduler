"""
Course offerings endpoints blueprint
"""
from flask import Blueprint, jsonify, current_app
from ..services.course_service import CourseService
from ..utils.response_helpers import success_response, error_response
from ..utils.validators import validate_semester_format, validate_department_code, validate_course_number

offerings_bp = Blueprint('offerings', __name__, url_prefix='/api/offerings')

@offerings_bp.route('/<semester>/<dept_code>/<course_number>', methods=['GET'])
def get_course_offerings(semester, dept_code, course_number):
    """Get course offerings for a specific semester, department, and course"""
    try:
        # Validate input parameters
        if not validate_semester_format(semester):
            return error_response('Invalid semester format. Expected: YY_SEASON (e.g., 25_FA)', 400)
        
        if not validate_department_code(dept_code.upper()):
            return error_response('Invalid department code format', 400)
        
        if not validate_course_number(course_number):
            return error_response('Invalid course number format', 400)
        
        course_service = CourseService(
            current_app.data_loader,
            current_app.config['DATA_DIR']
        )
        
        offerings = course_service.get_course_offerings(
            semester, dept_code.upper(), course_number
        )
        
        return success_response({
            'offerings': offerings,
            'count': len(offerings),
            'semester': semester,
            'department': dept_code.upper(),
            'course_number': course_number
        })
        
    except Exception as e:
        return error_response(f'Error loading course offerings: {str(e)}', 500)

@offerings_bp.route('/<semester>/<dept_code>', methods=['GET'])
def get_department_offerings(semester, dept_code):
    """Get all course offerings for a department in a specific semester"""
    try:
        # Validate input parameters
        if not validate_semester_format(semester):
            return error_response('Invalid semester format. Expected: YY_SEASON (e.g., 25_FA)', 400)
        
        if not validate_department_code(dept_code.upper()):
            return error_response('Invalid department code format', 400)
        
        # This would require extending CourseService to get all department offerings
        # For now, return a placeholder response
        return success_response({
            'message': 'Department offerings endpoint - to be implemented',
            'semester': semester,
            'department': dept_code.upper()
        })
        
    except Exception as e:
        return error_response(f'Error loading department offerings: {str(e)}', 500)