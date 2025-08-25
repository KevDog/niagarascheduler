"""
Health check endpoints blueprint
"""
import os
from flask import Blueprint, current_app
from ..utils.response_helpers import success_response, error_response

health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with system status"""
    try:
        # Basic health check
        health_data = {
            'status': 'healthy',
            'version': current_app.config['API_VERSION'],
            'api_title': current_app.config['API_TITLE'],
        }
        
        # Check data directory
        data_dir = current_app.config['DATA_DIR']
        if os.path.exists(data_dir):
            health_data['data_directory'] = 'accessible'
            
            # Check for key data subdirectories
            subdirs = ['departments', 'semesters']
            for subdir in subdirs:
                subdir_path = os.path.join(data_dir, subdir)
                health_data[f'{subdir}_directory'] = 'exists' if os.path.exists(subdir_path) else 'missing'
        else:
            health_data['data_directory'] = 'inaccessible'
        
        # Check template directory
        template_dir = current_app.config['TEMPLATE_DIR']
        health_data['template_directory'] = 'accessible' if os.path.exists(template_dir) else 'inaccessible'
        
        return success_response(health_data)
        
    except Exception as e:
        return error_response(f'Health check failed: {str(e)}', 500)

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with additional system information"""
    try:
        # Get basic health info
        basic_health = health_check()
        basic_data = basic_health[0].get_json()['data']
        
        # Add detailed information
        detailed_data = basic_data.copy()
        
        # Count departments
        try:
            dept_count = len(current_app.data_loader.get_all_departments())
            detailed_data['departments_count'] = dept_count
        except Exception:
            detailed_data['departments_count'] = 'error'
        
        # Count available semesters
        try:
            data_dir = current_app.config['DATA_DIR']
            semesters_dir = os.path.join(data_dir, 'semesters')
            if os.path.exists(semesters_dir):
                semester_folders = [f for f in os.listdir(semesters_dir) 
                                  if os.path.isdir(os.path.join(semesters_dir, f))]
                detailed_data['semesters_count'] = len(semester_folders)
                detailed_data['available_semesters'] = semester_folders
            else:
                detailed_data['semesters_count'] = 0
                detailed_data['available_semesters'] = []
        except Exception:
            detailed_data['semesters_count'] = 'error'
            detailed_data['available_semesters'] = 'error'
        
        return success_response(detailed_data)
        
    except Exception as e:
        return error_response(f'Detailed health check failed: {str(e)}', 500)