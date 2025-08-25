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
            
            # Create temporary file
            suffix = '.' + export_format
            temp_file = NamedTemporaryFile(suffix=suffix, delete=False)
            
            # Generate syllabus
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
                textbooks=textbooks,
                assignments=assignments,
                attendance_policy=attendance_policy,
                grading_policy=grading_policy,
                ai_policy=ai_policy,
                bibliography=bibliography
            )
            
            # Generate filename
            course_part = f"_{course_id}" if course_id else ""
            filename = f"{semester}{year}{course_part}_Syllabus.{export_format}"
            
            return {
                'file_path': temp_file.name,
                'filename': filename,
                'format': export_format,
                'course_id': course_id,
                'semester': semester,
                'year': year,
                'instructor': instructor_name
            }
            
        except Exception as e:
            raise Exception(f'Error exporting syllabus: {str(e)}')
    
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