"""
Request validation utilities
"""
import re
from typing import Dict, List, Any, Optional

def validate_semester_format(semester: str) -> bool:
    """
    Validate semester format (e.g., '25_FA', '26_SP')
    
    Args:
        semester: Semester string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^\d{2}_(FA|SP|SU|WI)$'
    return bool(re.match(pattern, semester))

def validate_department_code(dept_code: str) -> bool:
    """
    Validate department code format (2-4 uppercase letters)
    
    Args:
        dept_code: Department code to validate
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^[A-Z]{2,4}$'
    return bool(re.match(pattern, dept_code))

def validate_course_number(course_number: str) -> bool:
    """
    Validate course number format (3-4 digits)
    
    Args:
        course_number: Course number to validate
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^\d{3,4}$'
    return bool(re.match(pattern, course_number))

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, str]:
    """
    Validate that required fields are present and not empty
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
        
    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}
    
    for field in required_fields:
        if field not in data:
            errors[field] = f"{field} is required"
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            errors[field] = f"{field} cannot be empty"
    
    return errors

def validate_schedule_request(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate schedule generation request data
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}
    
    # Check required fields
    required_fields = ['semester_year']
    errors.update(validate_required_fields(data, required_fields))
    
    # Validate semester format
    semester_year = data.get('semester_year')
    if semester_year and not validate_semester_format(semester_year):
        errors['semester_year'] = "Invalid semester format. Expected format: YY_SEASON (e.g., 25_FA)"
    
    # Validate weekdays if provided
    weekdays = data.get('weekdays', [])
    if weekdays and not isinstance(weekdays, list):
        errors['weekdays'] = "Weekdays must be a list"
    elif weekdays:
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        invalid_days = [day for day in weekdays if day not in valid_days]
        if invalid_days:
            errors['weekdays'] = f"Invalid weekdays: {', '.join(invalid_days)}"
    
    return errors

def validate_syllabus_request(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate syllabus generation request data
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}
    
    # Check required fields
    required_fields = ['schedule', 'semester', 'year']
    errors.update(validate_required_fields(data, required_fields))
    
    # Validate schedule data
    schedule_data = data.get('schedule')
    if schedule_data and not isinstance(schedule_data, list):
        errors['schedule'] = "Schedule must be a list"
    
    # Validate export format if provided
    export_format = data.get('format')
    if export_format:
        valid_formats = ['docx', 'pdf', 'html', 'tex', 'md']
        if export_format not in valid_formats:
            errors['format'] = f"Invalid format. Supported formats: {', '.join(valid_formats)}"
    
    return errors