"""
Departments endpoints blueprint
"""
from flask import Blueprint, jsonify, current_app
from ..services.department_service import DepartmentService
from ..utils.response_helpers import success_response, error_response
from ..utils.validators import validate_department_code

departments_bp = Blueprint('departments', __name__, url_prefix='/api/departments')

@departments_bp.route('', methods=['GET'])
def get_departments():
    """Get list of all departments"""
    try:
        dept_service = DepartmentService(current_app.data_loader)
        departments = dept_service.get_all_departments()
        
        return success_response({
            'departments': departments,
            'count': len(departments)
        })
        
    except Exception as e:
        return error_response(f'Error loading departments: {str(e)}', 500)

@departments_bp.route('/<dept_code>', methods=['GET'])
def get_department(dept_code):
    """Get specific department information"""
    try:
        # Validate department code format
        if not validate_department_code(dept_code.upper()):
            return error_response('Invalid department code format', 400)
        
        dept_service = DepartmentService(current_app.data_loader)
        department = dept_service.get_department_by_code(dept_code.upper())
        
        if not department:
            return error_response('Department not found', 404)
        
        return success_response(department)
        
    except Exception as e:
        return error_response(f'Error loading department: {str(e)}', 500)

@departments_bp.route('/<dept_code>/stats', methods=['GET'])
def get_department_stats(dept_code):
    """Get department statistics"""
    try:
        # Validate department code format
        if not validate_department_code(dept_code.upper()):
            return error_response('Invalid department code format', 400)
        
        dept_service = DepartmentService(current_app.data_loader)
        
        if not dept_service.department_exists(dept_code.upper()):
            return error_response('Department not found', 404)
        
        course_count = dept_service.get_department_course_count(dept_code.upper())
        
        stats = {
            'department_code': dept_code.upper(),
            'course_count': course_count
        }
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'Error loading department stats: {str(e)}', 500)