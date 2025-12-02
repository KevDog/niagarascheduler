"""
Syllabus service for handling syllabus generation business logic
"""
import os
from tempfile import NamedTemporaryFile
from typing import List, Dict, Any, Optional
from core.markdown_processor import generate_syllabus_markdown, generate_syllabus

class SyllabusService:
    """Service class for syllabus generation operations"""
    
    def __init__(self, template_dir: str):
        """
        Initialize syllabus service
        
        Args:
            template_dir: Path to templates directory
        """
        self.template_dir = template_dir
    
    def generate_syllabus_markdown_content(self, schedule_data: List[str], semester: str, 
                                         year: str, course_id: str = '', 
                                         include_description: bool = False,
                                         instructor_name: str = 'TBD',
                                         office_hours: str = '', office_location: str = '',
                                         email_address: str = '', phone_number: str = '',
                                         textbooks: str = '', assignments: str = '',
                                         attendance_policy: str = '', grading_policy: str = '',
                                         ai_policy: str = '', bibliography: str = '') -> Dict[str, Any]:
        """
        Generate syllabus markdown content
        
        Args:
            schedule_data: List of schedule entries
            semester: Semester name
            year: Year
            course_id: Course ID (e.g., 'THR101')
            include_description: Whether to include course description
            instructor_name: Instructor name
            office_hours: Office hours information
            office_location: Office location information
            email_address: Email address
            phone_number: Phone number
            textbooks: Textbooks information
            assignments: Assignments information
            attendance_policy: Attendance policy text
            grading_policy: Grading policy text
            ai_policy: AI policy text
            bibliography: Bibliography text
        
        Returns:
            Dictionary with markdown content and metadata
            
        Raises:
            Exception: If markdown generation fails
        """
        try:
            markdown_content = generate_syllabus_markdown(
                schedule_data=schedule_data,
                semester=semester,
                year=year,
                course_id=course_id,
                include_description=include_description,
                instructor_name=instructor_name,
                office_hours=office_hours,
                office_location=office_location,
                email_address=email_address,
                phone_number=phone_number,
                textbooks=textbooks,
                assignments=assignments,
                attendance_policy=attendance_policy,
                grading_policy=grading_policy,
                ai_policy=ai_policy,
                bibliography=bibliography
            )
            
            return {
                'markdown': markdown_content,
                'course_id': course_id,
                'semester': semester,
                'year': year,
                'instructor': instructor_name,
                'metadata': {
                    'includes_description': include_description,
                    'has_textbooks': bool(textbooks.strip()),
                    'has_assignments': bool(assignments.strip()),
                    'has_attendance_policy': bool(attendance_policy.strip()),
                    'has_grading_policy': bool(grading_policy.strip()),
                    'has_ai_policy': bool(ai_policy.strip()),
                    'has_bibliography': bool(bibliography.strip())
                }
            }
            
        except Exception as e:
            raise Exception(f'Error generating syllabus markdown: {str(e)}')
    
    def export_syllabus_file(self, schedule_data: List[str], semester: str, year: str,
                            export_format: str = 'docx', course_id: str = '',
                            include_description: bool = False,
                            instructor_name: str = 'TBD',
                            office_hours: str = '', office_location: str = '',
                            email_address: str = '', phone_number: str = '',
                            textbooks: str = '', assignments: str = '',
                            attendance_policy: str = '', grading_policy: str = '',
                            ai_policy: str = '', bibliography: str = '') -> Dict[str, Any]:
        """
        Export syllabus to file format
        
        Args:
            schedule_data: List of schedule entries
            semester: Semester name
            year: Year
            export_format: Export format (docx, pdf, html, tex, md)
            course_id: Course ID
            include_description: Whether to include course description
            instructor_name: Instructor name
            office_hours: Office hours information
            office_location: Office location information
            email_address: Email address
            phone_number: Phone number
            textbooks: Textbooks information
            assignments: Assignments information
            attendance_policy: Attendance policy text
            grading_policy: Grading policy text
            ai_policy: AI policy text
            bibliography: Bibliography text
        
        Returns:
            Dictionary with file path and metadata
            
        Raises:
            Exception: If export fails
        """
        try:
            # Validate export format
            valid_formats = ['docx', 'pdf', 'html', 'tex', 'md']
            if export_format not in valid_formats:
                raise ValueError(f'Invalid export format: {export_format}. Supported: {valid_formats}')
            
            # Handle DOCX format with Word template
            if export_format == 'docx':
                from .word_template_service import create_word_syllabus
                
                # Load course data if available
                course_title = self._get_course_title(course_id)
                course_description = self._get_course_description(course_id)
                department_mission = self._get_department_mission(course_id)
                
                temp_file_path = create_word_syllabus(
                    schedule_data=schedule_data,
                    semester=semester,
                    year=year,
                    template_dir=self.template_dir,
                    course_id=course_id,
                    course_title=course_title,
                    course_description=course_description,
                    department_mission_statement=department_mission,
                    instructor_name=instructor_name,
                    office_hours=office_hours,
                    office_location=office_location,
                    email_address=email_address,
                    phone_number=phone_number,
                    textbooks=textbooks,
                    assignments=assignments,
                    attendance_policy=attendance_policy,
                    grading_policy=grading_policy,
                    ai_policy=ai_policy,
                    bibliography=bibliography,
                    include_description=include_description
                )
            else:
                # Create temporary file for other formats
                suffix = '.' + export_format
                temp_file = NamedTemporaryFile(suffix=suffix, delete=False)
                
                # Generate syllabus using existing method
                generate_syllabus(
                    schedule_data=schedule_data,
                    semester=semester,
                    year=year,
                    output_format=export_format,
                    template_dir=self.template_dir,
                    output_file=temp_file.name,
                    course_id=course_id,
                    include_description=include_description,
                    instructor_name=instructor_name,
                    office_hours=office_hours,
                    office_location=office_location,
                    email_address=email_address,
                    phone_number=phone_number,
                    textbooks=textbooks,
                    assignments=assignments,
                    attendance_policy=attendance_policy,
                    grading_policy=grading_policy,
                    ai_policy=ai_policy,
                    bibliography=bibliography
                )
                temp_file_path = temp_file.name
            
            # Generate filename
            course_part = f"_{course_id}" if course_id else ""
            filename = f"{semester}{year}{course_part}_Syllabus.{export_format}"
            
            return {
                'file_path': temp_file_path,
                'filename': filename,
                'format': export_format,
                'course_id': course_id,
                'semester': semester,
                'year': year,
                'instructor': instructor_name
            }
            
        except Exception as e:
            raise Exception(f'Error exporting syllabus: {str(e)}')
    
    def _get_course_title(self, course_id: str) -> str:
        """Get course title from course data"""
        if not course_id:
            return 'Course Title'
        
        try:
            from ..utils.data_loader import load_course_from_id
            course = load_course_from_id(course_id)
            return course.title if course else f'Course {course_id}'
        except:
            return f'Course {course_id}'
    
    def _get_course_description(self, course_id: str) -> str:
        """Get course description from course data"""
        if not course_id:
            return 'Course description will be provided.'
        
        try:
            from ..utils.data_loader import load_course_from_id
            course = load_course_from_id(course_id)
            return course.description if course and course.description else 'Course description will be provided.'
        except:
            return 'Course description will be provided.'
    
    def _get_department_mission(self, course_id: str) -> str:
        """Get department mission statement"""
        if not course_id or ' ' not in course_id:
            return 'This department is committed to providing excellent education and preparing students for success.'
        
        try:
            department_code = course_id.split()[0]
            from ..utils.data_loader import load_department
            department = load_department(department_code)
            return department.mission_statement if department and department.mission_statement else 'This department is committed to providing excellent education and preparing students for success.'
        except:
            return 'This department is committed to providing excellent education and preparing students for success.'
    
    def get_supported_export_formats(self) -> List[Dict[str, str]]:
        """
        Get list of supported export formats
        
        Returns:
            List of format dictionaries with code and description
        """
        return [
            {'code': 'docx', 'name': 'Microsoft Word', 'description': 'DOCX document'},
            {'code': 'pdf', 'name': 'PDF', 'description': 'Portable Document Format'},
            {'code': 'html', 'name': 'HTML', 'description': 'Web page'},
            {'code': 'tex', 'name': 'LaTeX', 'description': 'LaTeX source file'},
            {'code': 'md', 'name': 'Markdown', 'description': 'Markdown text file'}
        ]
    
    def validate_syllabus_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate syllabus generation data
        
        Args:
            data: Syllabus data dictionary
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Check required fields
        if not data.get('schedule'):
            errors['schedule'] = 'Schedule data is required'
        elif not isinstance(data['schedule'], list):
            errors['schedule'] = 'Schedule must be a list'
        
        if not data.get('semester'):
            errors['semester'] = 'Semester is required'
        
        if not data.get('year'):
            errors['year'] = 'Year is required'
        
        # Validate export format if provided
        export_format = data.get('format')
        if export_format:
            valid_formats = [fmt['code'] for fmt in self.get_supported_export_formats()]
            if export_format not in valid_formats:
                errors['format'] = f'Invalid format. Supported: {", ".join(valid_formats)}'
        
        return errors