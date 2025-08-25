"""
Department service for handling department-related business logic
"""
from typing import List, Dict, Optional, Any

class DepartmentService:
    """Service class for department operations"""
    
    def __init__(self, data_loader):
        """
        Initialize department service
        
        Args:
            data_loader: DepartmentDataLoader instance
        """
        self.data_loader = data_loader
    
    def get_all_departments(self) -> List[Dict[str, Any]]:
        """
        Get all departments with basic information
        
        Returns:
            List of department dictionaries
        """
        departments = self.data_loader.get_all_departments()
        dept_list = []
        
        for dept_code in departments:
            dept = self.data_loader.load_department(dept_code)
            if dept and dept.name:  # Only include departments with valid names
                dept_list.append({
                    'code': dept_code,
                    'name': dept.name,
                    'mission_statement': dept.mission_statement
                })
        
        # Sort departments by name for consistent ordering (handle None values)
        dept_list.sort(key=lambda x: x['name'] or '')
        return dept_list
    
    def get_department_by_code(self, dept_code: str) -> Optional[Dict[str, Any]]:
        """
        Get specific department with detailed information including courses
        
        Args:
            dept_code: Department code (e.g., 'THR', 'ACC')
        
        Returns:
            Department dictionary with courses, or None if not found
        """
        dept = self.data_loader.load_department(dept_code)
        if not dept:
            return None
            
        return {
            'code': dept_code,
            'name': dept.name,
            'mission_statement': dept.mission_statement,
            'office': getattr(dept, 'office', None),
            'course_listing_url': getattr(dept, 'course_listing_url', None),
            'courses': [
                {
                    'number': course.number,
                    'title': course.title,
                    'description': course.description,
                    'instructors': getattr(course, 'instructors', []),
                    'textbooks': getattr(course, 'textbooks', []),
                    'meeting_days': getattr(course, 'meeting_days', [])
                } for course in dept.courses
            ]
        }
    
    def department_exists(self, dept_code: str) -> bool:
        """
        Check if a department exists
        
        Args:
            dept_code: Department code to check
        
        Returns:
            True if department exists, False otherwise
        """
        return dept_code in self.data_loader.get_all_departments()
    
    def get_department_course_count(self, dept_code: str) -> int:
        """
        Get the number of courses in a department
        
        Args:
            dept_code: Department code
        
        Returns:
            Number of courses in the department, 0 if department not found
        """
        dept = self.data_loader.load_department(dept_code)
        return len(dept.courses) if dept else 0