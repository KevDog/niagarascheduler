"""
Response helper utilities for consistent API responses
"""
from flask import jsonify

def success_response(data, message=None, status_code=200):
    """
    Create a standard success response
    
    Args:
        data: The data to return
        message: Optional success message
        status_code: HTTP status code (default 200)
    
    Returns:
        Flask JSON response
    """
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

def error_response(message, status_code=400, error_code=None):
    """
    Create a standard error response
    
    Args:
        message: Error message
        status_code: HTTP status code (default 400)
        error_code: Optional application-specific error code
    
    Returns:
        Flask JSON response with error status
    """
    response = {
        'success': False,
        'error': {
            'message': message,
            'status_code': status_code
        }
    }
    if error_code:
        response['error']['code'] = error_code
    
    return jsonify(response), status_code

def validation_error_response(errors):
    """
    Create a validation error response
    
    Args:
        errors: Dictionary of field validation errors
    
    Returns:
        Flask JSON response with validation errors
    """
    return jsonify({
        'success': False,
        'error': {
            'message': 'Validation failed',
            'status_code': 422,
            'validation_errors': errors
        }
    }), 422