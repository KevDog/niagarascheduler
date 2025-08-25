"""
Course service for handling course-related business logic
"""
import os
import json
from typing import List, Dict, Optional, Any

class CourseService:
    """Service class for course operations"""
    
    def __init__(self, data_loader, data_dir: str):
        """
        Initialize course service
        
        Args:
            data_loader: DepartmentDataLoader instance
            data_dir: Path to data directory
        """
        self.data_loader = data_loader
        self.data_dir = data_dir
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific course information by course ID
        
        Args:
            course_id: Course ID (e.g., 'THR101', 'ACC111')
        
        Returns:
            Course dictionary or None if not found
        """
        course = self.data_loader.find_course(course_id)
        if not course:
            return None
        
        return {
            'id': course_id,
            'number': course.number,
            'title': course.title,
            'description': course.description,
            'instructors': getattr(course, 'instructors', []),
            'textbooks': getattr(course, 'textbooks', []),
            'meeting_days': getattr(course, 'meeting_days', []),
            'zoom_link': getattr(course, 'zoom_link', None)
        }
    
    def get_course_offerings(self, semester: str, dept_code: str, course_number: str) -> List[Dict[str, Any]]:
        """
        Get course offerings for a specific semester, department, and course
        
        Args:
            semester: Semester code (e.g., '25_FA')
            dept_code: Department code (e.g., 'THR')
            course_number: Course number (e.g., '101')
        
        Returns:
            List of course offering dictionaries
        """
        offerings_file = os.path.join(self.data_dir, 'semesters', semester, f'{dept_code}.json')
        
        if not os.path.exists(offerings_file):
            return []
        
        try:
            with open(offerings_file, 'r') as f:
                offerings_data = json.load(f)
            
            # Filter offerings by course number
            matching_offerings = []
            for offering in offerings_data:
                offering_number = offering.get('number', '')
                
                # Remove department prefix if present (e.g., "THR101A" -> "101A")
                if offering_number.startswith(dept_code):
                    clean_number = offering_number[len(dept_code):]
                else:
                    clean_number = offering_number
                
                # Match course number (e.g., "101" matches "101A", "101B", etc.)
                if clean_number.startswith(course_number):
                    section_letter = clean_number[len(course_number):] if len(clean_number) > len(course_number) else 'A'
                    
                    offering_data = {
                        'number': offering_number,
                        'name': offering.get('name', ''),
                        'credits': offering.get('credits', ''),
                        'section': section_letter,
                        'semester': semester,
                        'department': dept_code,
                        'course_number': course_number
                    }
                    
                    # Add schedule information if available
                    if 'days' in offering:
                        offering_data.update({
                            'days': offering.get('days', ''),
                            'start_time': offering.get('start_time', ''),
                            'end_time': offering.get('end_time', ''),
                            'delivery_type': offering.get('delivery_type', ''),
                            'availability': offering.get('availability', ''),
                            'instructor': offering.get('instructor', ''),
                            'location': offering.get('location', '')
                        })
                    
                    matching_offerings.append(offering_data)
            
            # Sort by section for consistent ordering
            matching_offerings.sort(key=lambda x: x['section'])
            return matching_offerings
            
        except Exception as e:
            raise Exception(f'Error loading offerings from {offerings_file}: {str(e)}')
    
    def get_available_semesters(self) -> List[str]:
        """
        Get list of available semesters from data directory
        
        Returns:
            List of semester codes
        """
        semesters_dir = os.path.join(self.data_dir, 'semesters')
        available_semesters = []
        
        if os.path.exists(semesters_dir):
            for semester_folder in os.listdir(semesters_dir):
                if os.path.isdir(os.path.join(semesters_dir, semester_folder)):
                    available_semesters.append(semester_folder)
        
        return sorted(available_semesters)
    
    def course_has_offerings(self, semester: str, dept_code: str, course_number: str) -> bool:
        """
        Check if a course has offerings in a specific semester
        
        Args:
            semester: Semester code
            dept_code: Department code  
            course_number: Course number
        
        Returns:
            True if course has offerings, False otherwise
        """
        offerings = self.get_course_offerings(semester, dept_code, course_number)
        return len(offerings) > 0