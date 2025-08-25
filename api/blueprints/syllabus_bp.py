"""
Syllabus generation endpoints blueprint
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from ..services.syllabus_service import SyllabusService
from ..utils.response_helpers import success_response, error_response, validation_error_response
from ..utils.validators import validate_syllabus_request

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/api')

@syllabus_bp.route('/generate-syllabus', methods=['POST'])
def generate_syllabus_endpoint():
    """Generate syllabus markdown content"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate request data
        validation_errors = validate_syllabus_request(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Extract parameters
        schedule_data = data['schedule']
        semester = data['semester']
        year = data['year']
        course_id = data.get('course_id', '')
        include_description = data.get('include_description', False)
        
        # Additional syllabus data with defaults
        instructor_name = data.get('instructor_name', 'TBD')
        textbooks = data.get('textbooks', '')
        assignments = data.get('assignments', '')
        attendance_policy = data.get('attendance_policy', '')
        grading_policy = data.get('grading_policy', '')
        ai_policy = data.get('ai_policy', '')
        bibliography = data.get('bibliography', '')
        
        # Generate syllabus markdown
        syllabus_service = SyllabusService(current_app.config['TEMPLATE_DIR'])
        result = syllabus_service.generate_syllabus_markdown_content(
            schedule_data=schedule_data,
            semester=semester,
            year=year,
            course_id=course_id,
            include_description=include_description,
            instructor_name=instructor_name,
            textbooks=textbooks,
            assignments=assignments,
            attendance_policy=attendance_policy,
            grading_policy=grading_policy,
            ai_policy=ai_policy,
            bibliography=bibliography
        )
        
        return success_response(result, 'Syllabus generated successfully')
        
    except Exception as e:
        return error_response(f'Error generating syllabus: {str(e)}', 500)

@syllabus_bp.route('/export-syllabus', methods=['POST'])
def export_syllabus_endpoint():
    """Export syllabus in specified format"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate request data
        validation_errors = validate_syllabus_request(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Extract parameters
        schedule_data = data['schedule']
        semester = data['semester']
        year = data['year']
        export_format = data.get('format', 'docx')
        course_id = data.get('course_id', '')
        include_description = data.get('include_description', False)
        
        # Additional syllabus data with defaults
        instructor_name = data.get('instructor_name', 'TBD')
        textbooks = data.get('textbooks', '')
        assignments = data.get('assignments', '')
        attendance_policy = data.get('attendance_policy', '')
        grading_policy = data.get('grading_policy', '')
        ai_policy = data.get('ai_policy', '')
        bibliography = data.get('bibliography', '')
        
        # Generate and export syllabus
        syllabus_service = SyllabusService(current_app.config['TEMPLATE_DIR'])
        result = syllabus_service.export_syllabus_file(
            schedule_data=schedule_data,
            semester=semester,
            year=year,
            export_format=export_format,
            course_id=course_id,
            include_description=include_description,
            instructor_name=instructor_name,
            textbooks=textbooks,
            assignments=assignments,
            attendance_policy=attendance_policy,
            grading_policy=grading_policy,
            ai_policy=ai_policy,
            bibliography=bibliography
        )
        
        return send_file(
            result['file_path'],
            as_attachment=True,
            download_name=result['filename']
        )
        
    except ValueError as e:
        return error_response(f'Invalid request data: {str(e)}', 400)
    except Exception as e:
        return error_response(f'Error exporting syllabus: {str(e)}', 500)

@syllabus_bp.route('/syllabus-formats', methods=['GET'])
def get_syllabus_formats():
    """Get supported syllabus export formats"""
    try:
        syllabus_service = SyllabusService(current_app.config['TEMPLATE_DIR'])
        formats = syllabus_service.get_supported_export_formats()
        
        return success_response({
            'formats': formats,
            'count': len(formats)
        })
        
    except Exception as e:
        return error_response(f'Error loading formats: {str(e)}', 500)